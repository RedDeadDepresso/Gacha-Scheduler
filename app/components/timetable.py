# coding: utf-8
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView, QWidget, QHBoxLayout
from qfluentwidgets import Action, TableWidget, RoundMenu, MenuAnimationType, CheckBox
from qfluentwidgets import FluentIcon as FIF
from ..common.config import cfg
from ..common.signal_bus import signalBus

CHECKBOX_COL_WIDTH = 48


class HeaderCheckBox(CheckBox):
    """CheckBox that cycles unchecked → checked → unchecked, 
    reserving partial state only for programmatic mixed-selection display."""

    def nextCheckState(self):
        if self.checkState() == Qt.CheckState.Checked:
            self.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.setCheckState(Qt.CheckState.Checked)


class TimeTable(TableWidget):

    selectionChanged_ = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        cfg.loadSchedule()
        signalBus.addScheduleSignal.connect(self.setTable)
        signalBus.removeScheduleSignal.connect(self.setTable)
        signalBus.removeGameSignal.connect(self.setTable)

        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.setColumnCount(3)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, CHECKBOX_COL_WIDTH)

        # Parent to viewport so it scrolls/clips correctly with the header
        self._headerCheck = HeaderCheckBox(self.horizontalHeader().viewport())
        self._headerCheck.setTristate(True)
        self._headerCheck.setFixedSize(20, 20)
        self._headerCheck.stateChanged.connect(self._onHeaderCheckChanged)

        # Reposition whenever the header geometry changes
        self.horizontalHeader().sectionResized.connect(lambda *_: self._positionHeaderCheck())
        self.horizontalHeader().geometriesChanged.connect(self._positionHeaderCheck)

        self.setTable()

        # Delay initial positioning until the widget is fully laid out
        QTimer.singleShot(0, self._positionHeaderCheck)

    def showEvent(self, event):
        super().showEvent(event)
        self._positionHeaderCheck()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._positionHeaderCheck()

    def _positionHeaderCheck(self):
        header = self.horizontalHeader()
        cb = self._headerCheck
        section_width = CHECKBOX_COL_WIDTH
        header_height = header.height()
        cb_w, cb_h = cb.width(), cb.height()
        x = (section_width - cb_w) // 2
        y = max(0, (header_height - cb_h) // 2)
        cb.move(x, y)
        cb.raise_()
        cb.show()

    def _makeCheckBox(self) -> QWidget:
        container = QWidget()
        container.setFixedHeight(self.verticalHeader().defaultSectionSize())
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cb = CheckBox()
        cb.stateChanged.connect(self._onRowCheckChanged)
        layout.addWidget(cb)
        return container

    def _onHeaderCheckChanged(self, state):
        if state == Qt.CheckState.PartiallyChecked.value:
            return
        checked = state == Qt.CheckState.Checked.value
        self._headerCheck.blockSignals(True)
        for row in range(self.rowCount()):
            cb = self._getRowCheckBox(row)
            if cb:
                cb.blockSignals(True)
                cb.setChecked(checked)
                cb.blockSignals(False)
        self._headerCheck.blockSignals(False)
        self.selectionChanged_.emit(self.selectedCount())

    def _onRowCheckChanged(self):
        count = self.selectedCount()
        self.selectionChanged_.emit(count)
        self._headerCheck.blockSignals(True)
        total = self.rowCount()
        if count == 0:
            self._headerCheck.setCheckState(Qt.CheckState.Unchecked)
        elif count == total:
            self._headerCheck.setCheckState(Qt.CheckState.Checked)
        else:
            self._headerCheck.setCheckState(Qt.CheckState.PartiallyChecked)
        self._headerCheck.blockSignals(False)

    def _getRowCheckBox(self, row) -> CheckBox | None:
        widget = self.cellWidget(row, 0)
        if widget:
            for child in widget.children():
                if isinstance(child, CheckBox):
                    return child
        return None

    def selectedCount(self) -> int:
        return sum(
            1 for row in range(self.rowCount())
            if (cb := self._getRowCheckBox(row)) and cb.isChecked()
        )

    def selectedEntries(self) -> list[tuple[str, str]]:
        entries = []
        for row in range(self.rowCount()):
            cb = self._getRowCheckBox(row)
            if cb and cb.isChecked():
                time = self.item(row, 1).text()
                game = self.item(row, 2).text()
                entries.append((time, game))
        return entries

    def removeSelected(self):
        for time, game in self.selectedEntries():
            cfg.removeSchedule(time, game)

    def contextMenuEvent(self, event):
        row = self.rowAt(event.pos().y())
        if row < 0:
            return
        contextMenu = RoundMenu(parent=self)
        remove = Action(FIF.DELETE, self.tr("Remove"))
        time = self.item(row, 1).text()
        game = self.item(row, 2).text()
        self.selectRow(row)
        remove.triggered.connect(lambda: cfg.removeSchedule(time, game))
        contextMenu.addAction(remove)
        contextMenu.exec(event.globalPos(), False, MenuAnimationType.NONE)

    def setTable(self):
        self.clear()
        self.setHorizontalHeaderLabels(['', self.tr('Time'), self.tr('Game')])
        self.setRowCount(len(cfg.schedule.value))
        for row, info in enumerate(cfg.schedule.value):
            self.setCellWidget(row, 0, self._makeCheckBox())
            for col in range(2):
                item = QTableWidgetItem(info[col])
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col + 1, item)

        self._headerCheck.blockSignals(True)
        self._headerCheck.setCheckState(Qt.CheckState.Unchecked)
        self._headerCheck.blockSignals(False)
        self._positionHeaderCheck()
        self.selectionChanged_.emit(0)