from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

from ..common.signal_bus import signalBus


class GameTimer(QTimer):
    def __init__(self, time, gameConfig):
        super().__init__()

        self.gameConfig = gameConfig
        self.time = datetime.strptime(time, "%H:%M:%S")

        gameConfig.stopTimers.connect(self.stop)
        self.timeout.connect(self.resetTimer)
        self.setInterval(self.diffMilliseconds)
        self.start()

    @property
    def diffMilliseconds(self):
        now = datetime.now()
        timeObject = self.time.replace(year=now.year, month=now.month, day=now.day)

        if timeObject < now:
            timeObject += timedelta(days=1)

        difference = timeObject - now
        diffMilliseconds = difference.total_seconds() * 1000

        return diffMilliseconds        
    
    def sendThreadSignal(self):
        print("Sending signal")
        signalBus.createThreadSignal.emit(self.gameConfig)
    
    def resetTimer(self):
        self.sendThreadSignal()
        self.setInterval(self.diffMilliseconds)
        self.start()
