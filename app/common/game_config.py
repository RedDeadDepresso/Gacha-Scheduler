from qfluentwidgets import ConfigItem


class GameConfig:

    def __init__(self, name, iconPath, gamePath, scriptPath, schedule=[]):
        self.name = name
        self.iconPath = ConfigItem(self.name, "IconPath", "")
        self.iconPath.value = iconPath

        self.gamePath = ConfigItem(self.name, "GamePath", "")
        self.gamePath.value = gamePath

        self.scriptPath = ConfigItem(self.name, "ScriptPath", "")
        self.scriptPath.value = scriptPath

        self.schedule = ConfigItem(self.name, "Schedule", [])
        self.schedule.value = schedule

        self.navigationGameWidget = None
        self.interface = None