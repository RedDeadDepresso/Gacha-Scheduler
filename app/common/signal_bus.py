# coding: utf-8
from PySide6.QtCore import QObject, Signal

from app.common.game_config import GameConfig


class SignalBus(QObject):
    """ Signal bus """

    micaEnableChanged = Signal(bool)

    addGameSignal = Signal(GameConfig)
    removeGameSignal = Signal(GameConfig)
    errorSignal = Signal(str)

    addScheduleSignal = Signal()
    removeScheduleSignal = Signal()

    createThreadSignal = Signal(GameConfig)
    checkUpdateSignal = Signal()
    hotkeyChangedSignal = Signal(str)
    hotkeyEnabledSignal = Signal(bool)

signalBus = SignalBus()