import os
import shlex
import subprocess
import time
import win32com.client

from ..common.config import cfg
from ..common.signal_bus import signalBus
from PySide6.QtCore import QRunnable
from win11toast import toast


class GameRunner(QRunnable):
    def __init__(self, gameConfig):
        super().__init__()
        self.gameConfig = gameConfig

    @property
    def gameName(self):
        return self.gameConfig.name

    @property
    def gamePath(self):
        return self.gameConfig.gamePath.value

    @property
    def iconPath(self):
        return self.gameConfig.iconPath.value

    @property
    def scriptPath(self):
        return self.gameConfig.scriptPath.value

    @property
    def scriptDelay(self):
        h, m, s = map(int, cfg.scriptDelay.value.split(':'))
        return (h * 3600) + (m * 60) + s

    @classmethod
    def extractArgs(cls, programPath):
        if programPath.endswith('.lnk'):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(programPath)
            programPath = os.path.abspath(shortcut.Targetpath)
            # Use shlex.split to correctly handle quoted arguments with spaces
            try:
                args = shlex.split(shortcut.Arguments)
            except ValueError:
                args = []
        else:
            args = []
        return programPath, args

    def showToast(self):
        iconPath = self.iconPath if os.path.exists(self.iconPath) else None
        return toast(
            self.gameName,
            f'{self.gameName} will open in 30 seconds',
            button='Cancel',
            icon=iconPath,
            duration='long'
        )

    @classmethod
    def openProgram(cls, path):
        try:
            directory = os.path.dirname(path)
            if path.endswith(".lnk"):
                path, args = cls.extractArgs(path)
                subprocess.Popen([path] + args, shell=True, cwd=directory,
                                 creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([path], shell=True, cwd=directory,
                                 creationflags=subprocess.DETACHED_PROCESS)
        except Exception as e:
            signalBus.errorSignal.emit(f"Failed to launch '{os.path.basename(path)}': {e}")

    def run(self):
        if not os.path.exists(self.gamePath):
            signalBus.errorSignal.emit(f"Game path not found for '{self.gameName}'")
            return

        if cfg.toastEnabled.value and \
                self.showToast() == {'arguments': 'http:Cancel', 'user_input': {}}:
            return

        self.openProgram(self.gamePath)

        # Only run the script if the game actually launched
        if self.scriptPath and not os.path.exists(self.scriptPath):
            signalBus.errorSignal.emit(f"Script path not found for '{self.gameName}'")
            return
        if os.path.exists(self.scriptPath):
            time.sleep(self.scriptDelay)
            self.openProgram(self.scriptPath)