# coding:utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from qfluentwidgets import PushButton, ScrollArea

from ..common.style_sheet import StyleSheet
from ..components.timetable import TimeTable
from ..components.time_message_box import TimeMessageBox


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
