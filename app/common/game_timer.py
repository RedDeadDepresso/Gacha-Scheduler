from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

class GameTimer:
    def __init__(self, time, gameConfig):
        self.time = datetime.strptime(time, "%H:%M:%S")
        self.timer = QTimer()

        gameConfig.stopTimers.connect(self.timer.stop)
        self.timer.timeout.connect(self.resetTimer)
        self.resetTimer()

    @property
    def diffMilliseconds(self):
        now = datetime.now()
        timeObject = self.time.replace(year=now.year, month=now.month, day=now.day)

        if timeObject < now:
            timeObject += timedelta(days=1)

        difference = timeObject - now
        diffMilliseconds = difference.total_seconds() * 1000

        return diffMilliseconds
    
    def resetTimer(self):
        self.timer.setInterval(self.diffMilliseconds)
        self.timer.start()
