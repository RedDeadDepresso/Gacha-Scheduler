# coding: utf-8
import sys

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout

from qfluentwidgets import TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet
from ..common.config import cfg
from ..common.game_config import GameConfig


class TimeTable(TableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        GameConfig.observers.append(self)

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
        self.setTable()

    def insertGame(self):
        pass

    def setTable(self):
        temp = []
        for game, gameConfig in cfg.games.items():
            for time in gameConfig.schedule.value:
                temp.append((time, game))

        temp.sort(key=lambda x: x[0])
        self.setRowCount(len(temp))
        for row, info in enumerate(temp):
            for col in range(2):
                print(info[col])
                self.setItem(row, col, QTableWidgetItem(info[col]))


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)

        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TimeTable(self)

        # NOTE: use custom item delegate
        # self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))

        # select row on right-click
        # self.tableView.setSelectRightClickedRow(True)

        # enable border
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)

        self.tableView.setWordWrap(False)

        self.setStyleSheet("Demo{background: rgb(255, 255, 255)} ")
        self.hBoxLayout.setContentsMargins(50, 30, 50, 30)
        self.hBoxLayout.addWidget(self.tableView)
        self.resize(735, 760)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()
