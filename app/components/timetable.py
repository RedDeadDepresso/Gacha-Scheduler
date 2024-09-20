# coding: utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView

from qfluentwidgets import Action, TableWidget, RoundMenu, MenuAnimationType
from qfluentwidgets import FluentIcon as FIF
from ..common.config import cfg
from ..common.signal_bus import signalBus


class TimeTable(TableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        cfg.loadSchedule()
        signalBus.addScheduleSignal.connect(self.setTable)
        signalBus.removeScheduleSignal.connect(self.setTable)
        signalBus.removeGameSignal.connect(self.setTable)

        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setBorderRadius(8)
        self.setBorderVisible(True)

        self.setColumnCount(2)
        self.setTable()

    def contextMenuEvent(self, event):
        contextMenu = RoundMenu(parent=self)
        remove = Action(FIF.DELETE, self.tr("Remove"))
        contextMenu.addAction(remove)

        # Get the row number of the right-clicked cell
        row = self.rowAt(event.pos().y())
        # Get the value of the first cell in the clicked row
        time = self.item(row, 0).text()
        # Get the value of the second cell in the clicked row
        game = self.item(row, 1).text()
        self.selectRow(row)
        remove.triggered.connect(lambda: cfg.removeSchedule(time, game))
        contextMenu.exec(event.globalPos(), False, MenuAnimationType.NONE)

    def setTable(self):
        self.clear()
        self.setHorizontalHeaderLabels([
            self.tr('Time'), self.tr('Game')
        ])
        self.setRowCount(len(cfg.schedule.value))
        for row, info in enumerate(cfg.schedule.value):
            for col in range(2):
                item = QTableWidgetItem(info[col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                self.setItem(row, col, item)

