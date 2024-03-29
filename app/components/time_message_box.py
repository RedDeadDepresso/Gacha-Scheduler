# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QDialog, QGraphicsOpacityEffect, QWidget, QHBoxLayout, QFileDialog, QVBoxLayout

from qfluentwidgets import ComboBox, TimeEdit, MessageBoxBase, SubtitleLabel, LineEdit, PushButton, setTheme, Theme
from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11


class TimeMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Edit Schedule'), self)
        self.gameComboBox = ComboBox(self)
        self.gameComboBox.addItems(list(cfg.games.keys()))
        self.comboBox.currentTextChanged.connect(print)
        self.timeEdit = TimeEdit(self)

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.gameComboBox)
        self.viewLayout.addWidget(self.timeEdit)

        # change the text of button
        self.yesButton.setText(self.tr('Save'))
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.setText(self.tr('Cancel'))
        self.widget.setMinimumWidth(500)

        # connect the file dialog buttons to methods


    def __onYesButtonClicked(self):
        self.accept()
        self.accepted.emit()

