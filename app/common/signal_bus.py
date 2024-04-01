# coding: utf-8
from PySide6.QtCore import QObject, Signal

from app.common.game_config import GameConfig


class SignalBus(QObject):
    """ Signal bus """

    switchToSampleCard = Signal(str, int)
    micaEnableChanged = Signal(bool)
    supportSignal = Signal()

    addGameSignal = Signal(GameConfig)
    removeGameSignal = Signal(GameConfig)
    
    addScheduleSignal = Signal()
    removeScheduleSignal = Signal()

    createThreadSignal = Signal(GameConfig)
    

signalBus = SignalBus()
