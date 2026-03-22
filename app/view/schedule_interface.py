# coding:utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout

from qfluentwidgets import PushButton, ScrollArea, MessageBox, FluentIcon as FIF

from ..common.style_sheet import StyleSheet
from ..components.timetable import TimeTable
from ..components.time_message_box import TimeMessageBox


class ScheduleInterface(ScrollArea):
    """ Schedule interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scheduleLabel = QLabel(self.tr("Schedule"), self)
        self.addButton = PushButton(FIF.ADD, self.tr("Add"), self)
        self.removeButton = PushButton(FIF.REMOVE, self.tr("Remove"), self)
        self.timeTable = TimeTable(self)

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidgetResizable(True)
        self.setObjectName('scheduleInterface')

        self.scheduleLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.removeButton.setDisabled(True)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        headerLayout = QHBoxLayout()
        headerLayout.addWidget(self.scheduleLabel, alignment=Qt.AlignmentFlag.AlignVCenter)
        headerLayout.addStretch()
        headerLayout.addWidget(self.addButton, alignment=Qt.AlignmentFlag.AlignVCenter)
        headerLayout.addWidget(self.removeButton, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(headerLayout)
        layout.addWidget(self.timeTable)
        layout.setStretchFactor(self.timeTable, 1)
        layout.setContentsMargins(36, 30, 30, 36)
        self.setLayout(layout)

    def showAddDialog(self):
        w = TimeMessageBox(self)
        w.exec()

    def showRemoveDialog(self):
        entries = self.timeTable.selectedEntries()
        if not entries:
            return

        names = "\n".join(f"• {time}  {game}" for time, game in entries)
        dialog = MessageBox(
            self.tr("Remove selected"),
            self.tr(f"Are you sure you want to remove {len(entries)} schedule entr{'y' if len(entries) == 1 else 'ies'}?\n\n{names}"),
            self
        )
        dialog.yesButton.setText(self.tr("Remove"))
        dialog.cancelButton.setText(self.tr("Cancel"))
        if dialog.exec():
            self.timeTable.removeSelected()

    def __connectSignalToSlot(self):
        self.addButton.clicked.connect(self.showAddDialog)
        self.removeButton.clicked.connect(self.showRemoveDialog)
        self.timeTable.selectionChanged_.connect(
            lambda count: self.removeButton.setDisabled(count == 0)
        )