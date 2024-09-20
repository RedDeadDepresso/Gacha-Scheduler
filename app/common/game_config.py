from PySide6.QtCore import QObject
from qfluentwidgets import ConfigItem


class GameConfig(QObject):

    def __init__(self, name, iconPath, gamePath, scriptPath):
        super().__init__()

        self.name = name
        self.iconPath = ConfigItem(self.name, "IconPath", "")
        self.iconPath.value = iconPath

        self.gamePath = ConfigItem(self.name, "GamePath", "")
        self.gamePath.value = gamePath

        self.scriptPath = ConfigItem(self.name, "ScriptPath", "")
        self.scriptPath.value = scriptPath

        self.timers = {}
        self.navigationGameWidget = None
        self.interface = None

    def killTimers(self):
        for timer in self.timers:
            timer.stop()
        self.timers.clear()

    def getTimer(self, time):
        for timer, timeSet in self.timers.items():
            if timeSet == time:
                return timer
        return None
