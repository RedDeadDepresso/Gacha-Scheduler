from datetime import datetime
from PySide6.QtCore import QObject
from qfluentwidgets import ConfigItem, ConfigSerializer
from typing import Union


class DateTimeSerializer(ConfigSerializer):
    def serialize(self, value):
        try:
            return datetime.strftime(value, "%d-%m-%y %H:%M:%S")
        except:
            return datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")
    
    def deserialize(self, value):
        try:
            return datetime.strptime(value, "%d-%m-%y %H:%M:%S")
        except:
            return datetime.now()


class GameConfig(QObject):
    def __init__(self, name: str, iconPath: str, gamePath: str, scriptPath: str, lastSession: Union[str, datetime]):
        super().__init__()

        self.name = name
        self.iconPath = ConfigItem(self.name, "IconPath", "")
        self.iconPath.value = iconPath

        self.gamePath = ConfigItem(self.name, "GamePath", "")
        self.gamePath.value = gamePath

        self.scriptPath = ConfigItem(self.name, "ScriptPath", "")
        self.scriptPath.value = scriptPath

        self.lastSession = ConfigItem(self.name, "LastSession", datetime.now(), serializer=DateTimeSerializer())
        if isinstance(lastSession, str):
            self.lastSession.value = datetime.strptime(lastSession, "%d-%m-%y %H:%M:%S")
        elif isinstance(lastSession, datetime):
            self.lastSession.value = lastSession
        else:
            self.lastSession.value = datetime.now()

        self.timers = dict()
        self.navigationGameWidget = None
        self.interface = None
        self.messageBox = None

    def killTimers(self):
        for timer in self.timers:
            timer.stop()
        self.timers.clear()

    def getTimer(self, time):
        for timer, timeSet in self.timers.items():
            if timeSet == time:
                return timer
        return None
    
    def allValues(self):
        return self.name, self.iconPath.value, self.gamePath.value, self.scriptPath.value
    
    def showMessageBox(self):
        from app.components.run_message_box import RunMessageBox
        RunMessageBox(self).show()