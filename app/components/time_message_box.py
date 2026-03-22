# coding:utf-8
from PySide6.QtCore import QTime
from qfluentwidgets import ComboBox, MessageBoxBase, SubtitleLabel, TimeEdit
from ..common.config import cfg


class TimeMessageBox(MessageBoxBase):
    """ Add schedule entry dialog """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Add Schedule'), self)
        self.gameComboBox = ComboBox(self)
        self.gameComboBox.addItems(list(cfg.games.keys()))
        self.timeEdit = TimeEdit(self)
        self.timeEdit.setTime(QTime.currentTime())
        self.timeEdit.setDisplayFormat("hh:mm:ss")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.gameComboBox)
        self.viewLayout.addWidget(self.timeEdit)

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


class EditTimeMessageBox(MessageBoxBase):
    """ Edit existing schedule entry dialog """

    def __init__(self, time: str, game: str, parent=None):
        super().__init__(parent)
        self._oldTime = time
        self._oldGame = game

        self.titleLabel = SubtitleLabel(self.tr('Edit Schedule'), self)
        self.gameComboBox = ComboBox(self)
        self.gameComboBox.addItems(list(cfg.games.keys()))
        self.timeEdit = TimeEdit(self)
        self.timeEdit.setDisplayFormat("hh:mm:ss")

        # Pre-fill with existing values
        self.gameComboBox.setCurrentText(game)
        self.timeEdit.setTime(QTime.fromString(time, "hh:mm:ss"))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.gameComboBox)
        self.viewLayout.addWidget(self.timeEdit)

        self.yesButton.setText(self.tr('Save'))
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.setText(self.tr('Cancel'))
        self.widget.setMinimumWidth(500)

    def __onYesButtonClicked(self):
        newGame = self.gameComboBox.currentText()
        newTime = self.timeEdit.text()
        if newTime == self._oldTime and newGame == self._oldGame:
            self.accept()
            return
        cfg.removeSchedule(self._oldTime, self._oldGame)
        cfg.addSchedule(newTime, newGame)
        self.accept()
        self.accepted.emit()