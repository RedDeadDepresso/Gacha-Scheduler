from PySide6.QtCore import QObject, Signal

from qfluentwidgets import ConfigItem


class GameConfig(QObject):
    stopTimers = Signal()

    def __init__(self, name, iconPath, gamePath, scriptPath):
        super().__init__()

        self.name = name
        self.iconPath = ConfigItem(self.name, "IconPath", "")
        self.iconPath.value = iconPath

        self.gamePath = ConfigItem(self.name, "GamePath", "")
        self.gamePath.value = gamePath

        self.scriptPath = ConfigItem(self.name, "ScriptPath", "")
        self.scriptPath.value = scriptPath

        self.navigationGameWidget = None
        self.interface = None