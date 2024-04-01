# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..components.timetable import TimeTable
from ..components.time_message_box import TimeMessageBox
from qfluentwidgets import PushButton

from PySide6.QtWidgets import QVBoxLayout

class ScheduleInterface(ScrollArea):
    """ Schedule interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # schedule label
        self.scheduleLabel = QLabel(self.tr("Schedule"), self)
        self.button = PushButton(self.tr("Add"), self)
        self.timeTable = TimeTable(self)

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidgetResizable(True)
        self.setObjectName('scheduleInterface')

        # initialize style sheet
        self.scheduleLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.scheduleLabel)
        layout.addWidget(self.button)
        layout.addWidget(self.timeTable)
        layout.setStretchFactor(self.timeTable, 1)
        layout.setContentsMargins(36, 30, 30, 36)
        self.setLayout(layout)

    def showMessageBox(self):
        w = TimeMessageBox(self)
        w.exec()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.button.clicked.connect(self.showMessageBox)
