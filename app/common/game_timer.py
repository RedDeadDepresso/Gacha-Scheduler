from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

from ..common.signal_bus import signalBus


class GameTimer(QTimer):
    def __init__(self, time, gameConfig):
        super().__init__()

        self.gameConfig = gameConfig
        self.time = datetime.strptime(time, "%H:%M:%S")

        self.timeout.connect(self.reset)
        self.setInterval(self.diffMilliseconds)

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
        signalBus.createThreadSignal.emit(self.gameConfig)
    
    def reset(self):
        self.stop()
        self.sendThreadSignal()
        self.setInterval(self.diffMilliseconds)
        self.start()
