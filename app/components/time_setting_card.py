# coding:utf-8
from typing import Union

from PySide6.QtCore import Qt, Signal, QTime
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QPushButton
from PySide6.QtSvgWidgets import QSvgWidget

from qfluentwidgets import FluentIconBase, qconfig, SettingCard, TimePicker


class TimeSettingCard(SettingCard):
    """ Setting card with a time edit """

    timeChanged = Signal(QTime)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
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
        self.configItem = configItem
        self.timePicker = TimePicker(self, showSeconds=True)

        time = QTime.fromString(configItem.value, 'hh:mm:ss')
        self.timePicker.setTime(time)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.timePicker, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        configItem.valueChanged.connect(self.setTime)
        self.timePicker.timeChanged.connect(self.__onTimeChanged)

    def __onTimeChanged(self, time: QTime):
        """ time edit value changed slot """
        self.setTime(time)
        self.timeChanged.emit(time)

    def setTime(self, time):
        if isinstance(time, str):
            time = QTime.fromString(time, 'hh:mm:ss')
            self.timePicker.setTime(time)
        elif isinstance(time, QTime):
            qconfig.set(self.configItem, time.toString('hh:mm:ss'))
