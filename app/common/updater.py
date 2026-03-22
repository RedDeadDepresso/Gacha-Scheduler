# coding: utf-8
import os
import sys
import ssl
import json
import zipfile
import tempfile

import certifi
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from packaging.version import Version
from PySide6.QtCore import QRunnable, QObject, Signal, Slot, QThreadPool
from qfluentwidgets import MessageBox, ProgressBar, CaptionLabel

from app.common.config import VERSION, REPO_URL, cfg


def _ssl_context():
    return ssl.create_default_context(cafile=certifi.where())


GITHUB_API = REPO_URL.replace("https://github.com/", "https://api.github.com/repos/") + "/releases/latest"


class UpdaterSignals(QObject):
    updateAvailable = Signal(str, str)  # (latest_version, download_url)
    noUpdate = Signal()
    error = Signal(str)
    progress = Signal(int, int)          # (bytes_downloaded, total_bytes)
    extracting = Signal()


class UpdateChecker(QRunnable):
    """Checks GitHub releases API for a newer version. Runs in a thread."""

    def __init__(self):
        super().__init__()
        self.setAutoDelete(False)
        self.signals = UpdaterSignals()

    def run(self):
        try:
            with urlopen(GITHUB_API, timeout=5, context=_ssl_context()) as response:
                data = json.loads(response.read().decode())

            latest = data.get("tag_name", "").lstrip("v")
            if not latest:
                self.signals.error.emit("Could not parse release version.")
                return

            assets = data.get("assets", [])
            zip_url = next(
                (a["browser_download_url"] for a in assets if a["name"].endswith(".zip")),
                None
            )

            if not zip_url:
                self.signals.error.emit("No zip asset found in latest release.")
                return

            # Re-read version at check time so we always get the installed version
            # rather than the stale module-level constant from before an update
            from importlib.metadata import version as pkg_version, PackageNotFoundError
            try:
                current = pkg_version("gacha-scheduler")
            except PackageNotFoundError:
                current = VERSION

            if Version(latest) > Version(current):
                self.signals.updateAvailable.emit(latest, zip_url)
            else:
                self.signals.noUpdate.emit()

        except URLError as e:
            self.signals.error.emit(f"Network error: {e.reason}")
        except Exception as e:
            self.signals.error.emit(str(e))


class UpdateInstaller(QRunnable):
    """Downloads and extracts the update zip, then writes a PowerShell helper."""

    def __init__(self, download_url: str):
        super().__init__()
        self.setAutoDelete(False)
        self.download_url = download_url
        self.signals = UpdaterSignals()

    def run(self):
        try:
            tmp_dir = Path(tempfile.mkdtemp(prefix="gacha_update_"))
            zip_path = tmp_dir / "update.zip"

            with urlopen(self.download_url, context=_ssl_context()) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                with open(zip_path, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.signals.progress.emit(downloaded, total)

            self.signals.extracting.emit()

            staging_dir = tmp_dir / "staging"
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(staging_dir)

            install_dir  = Path(sys.executable).parent
            helper_path  = tmp_dir / "_update_helper.ps1"
            executable   = install_dir / "Gacha-Scheduler.exe"
            log_path     = tmp_dir / "update.log"

            staging_win = str(staging_dir).replace("/", "\\")
            target_win  = str(install_dir).replace("/", "\\")
            exe_win     = str(executable).replace("/", "\\")
            log_win     = str(log_path).replace("/", "\\")

            helper_script = f"""
$pid_to_wait = {os.getpid()}
$staging     = '{staging_win}'
$target      = '{target_win}'
$executable  = '{exe_win}'
$log         = '{log_win}'

function Log($msg) {{
    $ts = Get-Date -Format 'HH:mm:ss'
    Add-Content -Path $log -Value "[$ts] $msg"
}}

Log "Helper started. Waiting for PID $pid_to_wait to exit."

try {{
    $proc = Get-Process -Id $pid_to_wait -ErrorAction SilentlyContinue
    if ($proc) {{
        Log "Process found, waiting..."
        $proc.WaitForExit(30000)
        Log "Process exited."
    }} else {{
        Log "Process already gone."
    }}
}} catch {{
    Log "Wait error: $_"
}}

Start-Sleep -Seconds 2

Log "Copying files from staging to target"
$errors = 0
Get-ChildItem -Path $staging | ForEach-Object {{
    $dest = Join-Path $target $_.Name
    try {{
        if ($_.PSIsContainer) {{
            if ($_.Name -eq "icons") {{
                # Only copy icons that don't already exist — preserve user-added icons
                if (-not (Test-Path $dest)) {{
                    New-Item -ItemType Directory -Path $dest -Force | Out-Null
                }}
                Get-ChildItem -Path $_.FullName | ForEach-Object {{
                    $iconDest = Join-Path $dest $_.Name
                    if (-not (Test-Path $iconDest)) {{
                        Copy-Item -Path $_.FullName -Destination $iconDest -Force
                        Log "Added new icon: $($_.Name)"
                    }}
                }}
            }} else {{
                # Mirror all other directories so removed files are cleaned up
                $result = robocopy $_.FullName $dest /MIR /IS /IT /IM /NFL /NDL 2>&1
                if ($LASTEXITCODE -le 7) {{
                    Log "Mirrored dir: $($_.Name)"
                }} else {{
                    Log "ERROR mirroring dir $($_.Name): exit code $LASTEXITCODE"
                    $errors++
                }}
            }}
        }} else {{
            Copy-Item -Path $_.FullName -Destination $dest -Force
            Log "Copied file: $($_.Name)"
        }}
    }} catch {{
        Log "ERROR copying $($_.Name): $_"
        $errors++
    }}
}}

if ($errors -eq 0) {{
    Log "Copy successful. Launching $executable"
    Start-Process $executable
    Log "Launched."
}} else {{
    Log "ERROR: $errors item(s) failed to copy"
}}
"""
            helper_path.write_text(helper_script, encoding="utf-8")
            self.signals.updateAvailable.emit("done", str(helper_path))

        except Exception as e:
            self.signals.error.emit(str(e))


class DownloadDialog(MessageBox):
    """Modal dialog showing download progress."""

    def __init__(self, parent=None):
        super().__init__(
            "Downloading update",
            "Please wait while the update is being downloaded...",
            parent
        )
        self.yesButton.hide()
        self.cancelButton.hide()

        self.statusLabel = CaptionLabel("Starting download...", self)
        self.progressBar = ProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        self.textLayout.addWidget(self.statusLabel)
        self.textLayout.addWidget(self.progressBar)

    @Slot(int, int)
    def onProgress(self, downloaded: int, total: int):
        if total > 0:
            self.progressBar.setValue(int(downloaded / total * 100))
            self.statusLabel.setText(
                f"Downloading... {downloaded / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB"
            )
        else:
            self.progressBar.setRange(0, 0)
            self.statusLabel.setText(f"Downloading... {downloaded / (1024*1024):.1f} MB")

    @Slot()
    def onExtracting(self):
        self.progressBar.setRange(0, 0)
        self.statusLabel.setText("Extracting...")


class UpdateManager:
    """
    Coordinates the check → prompt → install → restart flow.
    Call check() after the main window is shown.
    """

    def __init__(self, thread_pool: QThreadPool, main_window):
        self.thread_pool = thread_pool
        self.main_window = main_window

        from app.common.signal_bus import signalBus
        signalBus.checkUpdateSignal.connect(self._onManualCheck)

    def check(self):
        """Automatic check on startup — respects checkUpdateAtStartUp setting."""
        if not cfg.get(cfg.checkUpdateAtStartUp):
            return
        self._run_checker(manual=False)

    def _onManualCheck(self):
        """Manual check triggered from the settings About card."""
        self._run_checker(manual=True)

    def _run_checker(self, manual: bool):
        checker = UpdateChecker()
        checker.signals.updateAvailable.connect(self._onUpdateAvailable)
        if manual:
            checker.signals.noUpdate.connect(self._onNoUpdate)
            checker.signals.error.connect(self._onCheckError)
        self.thread_pool.start(checker)

    @Slot(str, str)
    def _onUpdateAvailable(self, latest_version: str, download_url: str):
        dialog = MessageBox(
            f"Update available — v{latest_version}",
            f"A new version of Gacha Scheduler is available (you have v{VERSION}).\n\n"
            "Do you want to download and install it now?\n"
            "The application will restart automatically.",
            self.main_window
        )
        dialog.yesButton.setText("Update")
        dialog.cancelButton.setText("Later")

        if dialog.exec():
            self._install(download_url)

    def _install(self, download_url: str):
        self._download_dialog = DownloadDialog(self.main_window)

        installer = UpdateInstaller(download_url)
        installer.signals.progress.connect(self._download_dialog.onProgress)
        installer.signals.extracting.connect(self._download_dialog.onExtracting)
        installer.signals.updateAvailable.connect(self._onInstallDone)
        installer.signals.error.connect(self._onInstallError)
        installer.signals.error.connect(lambda _: self._download_dialog.close())

        self.thread_pool.start(installer)
        self._download_dialog.exec()

    @Slot(str, str)
    def _onInstallDone(self, _, helper_path: str):
        self._download_dialog.close()
        dialog = MessageBox(
            "Update ready",
            "The update has been downloaded. Gacha Scheduler will now close and apply the update, then restart automatically.",
            self.main_window
        )
        dialog.cancelButton.hide()
        dialog.exec()
        self._restart(helper_path)

    @staticmethod
    def _restart(helper_path: str):
        import subprocess
        import time
        cmd = f'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "{helper_path}"'
        subprocess.Popen(
            f'cmd.exe /c start "" /b {cmd}',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(0.5)
        sys.exit(0)

    @Slot(str)
    def _onInstallError(self, error: str):
        dialog = MessageBox(
            "Update failed",
            f"An error occurred while installing the update:\n\n{error}\n\n"
            "You can download the update manually from the releases page.",
            self.main_window
        )
        dialog.cancelButton.hide()
        dialog.exec()

    @Slot()
    def _onNoUpdate(self):
        dialog = MessageBox(
            "No updates available",
            f"You are already on the latest version (v{VERSION}).",
            self.main_window
        )
        dialog.cancelButton.hide()
        dialog.exec()

    @Slot(str)
    def _onCheckError(self, error: str):
        dialog = MessageBox(
            "Update check failed",
            f"Could not check for updates:\n\n{error}",
            self.main_window
        )
        dialog.cancelButton.hide()
        dialog.exec()