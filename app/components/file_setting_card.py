import os
import pathlib
import subprocess

from app.common.game_runner import GameRunner
from enum import Enum
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import SettingCard, FluentIconBase, FluentIcon, CommandBar, Action, LineEdit, LineEditButton
from typing import Union
from ..common.config import cfg


def _executable_extensions():
    """Build the set of executable extensions from Windows PATHEXT plus .lnk and .py."""
    pathext = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    exts = {e.lower() for e in pathext.split(";")}
    exts.update({".lnk", ".py"})
    return exts


def _executable_filter():
    """Build a QFileDialog filter string from executable extensions."""
    exts = _executable_extensions()
    patterns = " ".join(f"*{e}" for e in sorted(exts))
    return f"Executable Files ({patterns})"


class FileType(Enum):
    EXE = {
        "dialogCaption": "Add Executable",
        "dialogfilter": None,   # built dynamically via _executable_filter()
        "extensions": None      # built dynamically via _executable_extensions()
    }
    IMAGE = {
        "dialogCaption": "Add Icon",
        "dialogfilter": "Images (*.png *.xpm *.jpg *.webp)",
        "extensions": {".png", ".xpm", ".jpg", ".webp"}
    }

    @property
    def dialogCaption(self):
        return self.value["dialogCaption"]

    @property
    def dialogfilter(self):
        if self.value["dialogfilter"] is None:
            return _executable_filter()
        return self.value["dialogfilter"]

    @property
    def extensions(self):
        if self.value["extensions"] is None:
            return _executable_extensions()
        return self.value["extensions"]
    

class FileLineEdit(LineEdit):
    """ Search line edit """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validButton = LineEditButton(FluentIcon.ACCEPT, self)
        self.hBoxLayout.addWidget(self.validButton, 0, Qt.AlignRight)
        self.setTextMargins(0, 0, 59, 0)

    def setValid(self, value: bool):
        if value:
            self.validButton._icon = FluentIcon.ACCEPT
        else:
            self.validButton._icon = FluentIcon.CLOSE


class FileSettingCard(SettingCard):
    validPathChanged = Signal(str)

    def __init__(self, fileType: FileType, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        configItem: TimeConfigItem
            configuration item operated by the card

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.fileType = fileType
        self.configItem = configItem
        self.lineEdit = FileLineEdit()
        self.lineEdit.setText(configItem.value)
        
        self.__initCommandBar()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initCommandBar(self):
        self.commandBar = CommandBar()
        if self.fileType == FileType.EXE:
            runAction = Action(FluentIcon.PLAY, 'Run')
            runAction.triggered.connect(self.run)
            self.commandBar.addHiddenAction(runAction)

        explorerAction = Action(FluentIcon.FOLDER, 'View in Explorer')
        explorerAction.triggered.connect(self.openExplorer)
        self.commandBar.addHiddenAction(explorerAction)

        browseAction = Action(FluentIcon.EDIT, 'Browse')
        browseAction.triggered.connect(self.browse)
        self.commandBar.addHiddenAction(browseAction)

    def __initLayout(self):
        self.setFixedHeight(70)
        self.vBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.setStretch(2, 10)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.commandBar, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def __connectSignalToSlot(self):
        self.lineEdit.textChanged.connect(self.pathValid)

    def pathValid(self, text):
        if not text:
            cfg.set(self.configItem, "")
            self.lineEdit.setValid(True)
            return

        path = pathlib.Path(text)
        if path.is_absolute() and path.is_file() and path.exists() and path.suffix.lower() in self.fileType.extensions:
            cfg.set(self.configItem, text)
            self.lineEdit.setValid(True)
            self.validPathChanged.emit(text)
        else:
            self.lineEdit.setValid(False)

    def run(self):
        if self.configItem.value:
            GameRunner.openProgram(self.configItem.value)

    def openExplorer(self):
        if self.configItem.value:
            file_path = os.path.normpath(self.configItem.value)        
            subprocess.Popen(f'explorer /select,"{file_path}"')

    def browse(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            self.fileType.dialogCaption,
            "",
            self.fileType.dialogfilter,
            options=QFileDialog.Option.DontResolveSymlinks
        )

        if not fileName or cfg.get(self.configItem) == fileName:
            return
        self.lineEdit.setText(fileName)