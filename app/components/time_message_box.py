# coding:utf-8
from PySide6.QtCore import QTime
from qfluentwidgets import ComboBox, MessageBoxBase, SubtitleLabel, TimeEdit
from ..common.config import cfg


class TimeMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Edit Schedule'), self)
        self.gameComboBox = ComboBox(self)
        self.gameComboBox.addItems(list(cfg.games.keys()))
        self.timeEdit = TimeEdit(self)
        self.timeEdit.setTime(QTime.currentTime())
        self.timeEdit.setDisplayFormat("hh:mm:ss")

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

    def __onYesButtonClicked(self):
        game = self.gameComboBox.currentText()
        time = self.timeEdit.text()
        if time:
            cfg.addSchedule(time, game)
            self.accept()
            self.accepted.emit()