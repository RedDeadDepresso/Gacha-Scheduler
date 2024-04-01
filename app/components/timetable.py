# coding: utf-8
import sys

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QPalette, QAction
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, QHeaderView, QMenu

from qfluentwidgets import TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet
from ..common.config import cfg
from ..common.signal_bus import signalBus


class TimeTable(TableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        contextMenu = QMenu(self)

        remove = QAction("Remove", self)
        contextMenu.addAction(remove)

        # Get the row number of the right-clicked cell
        row = self.rowAt(event.pos().y())
        # Get the value of the first cell in the clicked row
        time = self.item(row, 0).text()
        # Get the value of the second cell in the clicked row
        game = self.item(row, 1).text()

        # Now you can use the values in your slots
        remove.triggered.connect(lambda: cfg.removeSchedule(time, game))

        contextMenu.exec_(event.globalPos())

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

