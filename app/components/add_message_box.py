# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QDialog, QGraphicsOpacityEffect, QWidget, QHBoxLayout, QFileDialog

from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PushButton, setTheme, Theme
from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11


class AddMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Add Game'), self)
        self.nameLineEdit = LineEdit(self)

        # Create two QHBoxLayouts, each containing a LineEdit and a PushButton
        self.iconLayout = QHBoxLayout()
        self.iconLineEdit = LineEdit(self)
        self.iconDialogButton = PushButton(self.tr('Browse'), self)
        self.iconLayout.addWidget(self.iconLineEdit)
        self.iconLayout.addWidget(self.iconDialogButton)

        self.gameLayout = QHBoxLayout()
        self.gameLineEdit = LineEdit(self)
        self.gameDialogButton = PushButton(self.tr('Browse'), self)
        self.gameLayout.addWidget(self.gameLineEdit)
        self.gameLayout.addWidget(self.gameDialogButton)

        self.scriptLayout = QHBoxLayout()
        self.scriptLineEdit = LineEdit(self)
        self.scriptDialogButton = PushButton(self.tr('Browse'), self)
        self.scriptLayout.addWidget(self.scriptLineEdit)
        self.scriptLayout.addWidget(self.scriptDialogButton)

        self.nameLineEdit.setPlaceholderText(self.tr('Enter name of the game*'))
        self.iconLineEdit.setPlaceholderText(self.tr('Enter icon path'))
        self.gameLineEdit.setPlaceholderText(self.tr('Enter game path*'))
        self.scriptLineEdit.setPlaceholderText(self.tr('Enter script path'))

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameLineEdit)
        self.viewLayout.addLayout(self.iconLayout)
        self.viewLayout.addLayout(self.gameLayout)
        self.viewLayout.addLayout(self.scriptLayout)

        # change the text of button
        self.yesButton.setText(self.tr('Save'))
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.setText(self.tr('Cancel'))

        self.widget.setMinimumWidth(500)

        # connect the file dialog buttons to methods
        self.iconDialogButton.clicked.connect(lambda: self.openImageDialog(self.iconLineEdit))
        self.gameDialogButton.clicked.connect(lambda: self.openExeDialog(self.gameLineEdit))
        self.scriptDialogButton.clicked.connect(lambda: self.openExeDialog(self.scriptLineEdit))

    @property
    def name(self):
        return self.nameLineEdit.text()
    
    @property
    def iconPath(self):
        return self.iconLineEdit.text()
    
    @property
    def gamePath(self):
        return self.gameLineEdit.text()
    
    @property
    def scriptPath(self):
        return self.scriptLineEdit.text()

    def openImageDialog(self, lineEdit):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Add Icon", "", "Images (*.png *.xpm *.jpg)", options=options)
        if fileName:
            lineEdit.setText(fileName)  # update the second LineEdit with the selected file

    def openExeDialog(self, lineEdit):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Add Executable", "", "Executable Files (*.exe *.py)", options=options)
        if fileName:
            lineEdit.setText(fileName)

    def validateName(self):
        if cfg.getGame(self.name) is None:
            self.nameLineEdit.setStyleSheet("border: 1px solid red;")
            return True
        else:
            self.lineEdit.setStyleSheet("")
        
    def validatePaths(self):
        valid = True
        for lineEdit in [self.iconLineEdit, self.gameLineEdit, self.scriptLineEdit]:
            path = lineEdit.text()
            if lineEdit is self.gameLineEdit and not os.path.exists(path):
                lineEdit.setStyleSheet("border: 1px solid red;")
                valid = False
            elif path and not os.path.exists(path):
                lineEdit.setStyleSheet("border: 1px solid red;")
                valid = False
            else:
                lineEdit.setStyleSheet("")

        return valid

    def __onYesButtonClicked(self):
        if self.validateName() and self.validatePaths():
            self.accept()
            self.accepted.emit()

            cfg.addGame(
                self.name, 
                self.iconPath, 
                self.gamePath, 
                self.scriptPath
            )

