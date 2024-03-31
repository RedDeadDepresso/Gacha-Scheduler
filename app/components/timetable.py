# coding: utf-8
import sys

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout

from qfluentwidgets import TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet
from ..common.config import cfg
from ..common.signal_bus import signalBus


class TimeTable(TableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels([
            self.tr('Time'), self.tr('Game')
        ])
        self.setTable()

    def addGame(self, gameConfig):
        pass

    def removeGame(self, gameConfig):
        pass

    def insertGame(self):
        pass

    def setTable(self):
        self.clear()
        self.setRowCount(len(cfg.schedule.value))
        for row, info in enumerate(cfg.schedule.value):
            for col in range(2):
                self.setItem(row, col, QTableWidgetItem(info[col]))