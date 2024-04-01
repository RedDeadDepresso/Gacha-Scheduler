# coding:utf-8
import bisect
import json
import sys
import types

from datetime import datetime

from enum import Enum

from pathlib import Path

from PySide6.QtCore import QLocale, Signal
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, Theme, FolderValidator, ConfigSerializer, __version__, exceptionHandler)

from app.common.game_config import GameConfig
from app.common.game_timer import GameTimer
from app.common.signal_bus import signalBus


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class ScheduleSerializer(ConfigSerializer):
    def game_valid(self, input_str):
        return input_str in cfg.games
    
    def is_time_format(self, input_str):
        try:
            datetime.strptime(input_str, '%H:%M:%S')
            return True
        except ValueError:
            return False
    
    def validate(self, element):
        if isinstance(element, list) and len(element) == 2:
            if self.is_time_format(element[0]) and self.game_valid(element[1]):
                time = element[0]
                gameConfig = cfg.games[element[1]]
                GameTimer(time, gameConfig)
                return True
        return False

    def serialize(self, value):
        return value

    def deserialize(self, value: list[str, str]):
        if isinstance(value, list) and len(value) > 0:
            return [x for x in value if self.validate(x)].sort()
        else: 
            return []
        
    def correct(self, value):
        return value


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """
    
    # games
    toastEnabled = ConfigItem("Games", "ToastEnabled", True, BoolValidator())
    messageBoxEnabled = ConfigItem("Games", "MessageBoxEnabled", True, BoolValidator())
    scriptDelay = ConfigItem("Games", "ScriptDelay", '00:30')
    schedule = ConfigItem("Games", "Schedule", [], ScheduleSerializer())

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())

    def __init__(self):
        super().__init__()
        self.games = {}

    def __addItem(self, group, name, value):
        item_name = group + name
        setattr(self.__class__, item_name, value)

    def __removeItem(self, group, name):
        """ remove a config item

        Parameters
        ----------
        item: ConfigItem
            config item to be removed
        """
        # Check if the item exists
        item_name = group + name
        delattr(self.__class__, item_name)

    def addGame(self, name, iconPath, gamePath, scriptPath, save=True):
        try:
            gameConfig = GameConfig(name, iconPath, gamePath, scriptPath)
            self.__addItem(name, 'IconPath', gameConfig.iconPath)
            self.__addItem(name, 'GamePath', gameConfig.gamePath)
            self.__addItem(name, 'ScriptPath', gameConfig.scriptPath)
            if save:
                self.save()
            self.games[name] = gameConfig
            signalBus.addGameSignal.emit(gameConfig)
        except Exception as e:
            print(e)

    def getGame(self, name):
        return self.games.get(name)

    def removeGame(self, gameConfig):
        try:
            gameConfig.stopTimers.emit()
            name = gameConfig.name
            self.schedule.value = [x for x in self.schedule.value if x[1] != name]
            self.games.pop(name)
            signalBus.removeGameSignal.emit(gameConfig)
            self.__removeItem(name, 'IconPath')
            self.__removeItem(name, 'GamePath')
            self.__removeItem(name, 'ScriptPath')
            self.save()
        except Exception as e:
            print(e)

    def addSchedule(self, time, gameName):
        if gameName in self.games:
            entry = [time, gameName]
            bisect.insort(self.__class__.schedule.value, entry, key=lambda x: x[0])
            gameConfig = self.games[gameName]
            GameTimer(time, gameConfig)
            self.save()
            signalBus.addScheduleSignal.emit()
            return True
        return False

    def removeSchedule(self, time, game):
        entry = [time, game]
        self.__class__.schedule.value.remove(entry)
        self.save()
        signalBus.removeScheduleSignal.emit()


def customload(self, file=None, config=None):
    """ load config

    Parameters
    ----------
    file: str or Path
        the path of json config file

    config: Config
        config object to be initialized
    """
    if isinstance(config, Config):
        self._cfg = config
        self._cfg.themeChanged.connect(self.themeChanged)

    if isinstance(file, (str, Path)):
        self._cfg.file = Path(file)

    try:
        with open(self._cfg.file, encoding="utf-8") as f:
            cfg = json.load(f)
    except:
        cfg = {}

    # map config items'key to item
    items = {}
    for name in dir(self._cfg.__class__):
        item = getattr(self._cfg.__class__, name)
        if isinstance(item, ConfigItem):
            items[item.key] = item

    # update the value of config item
    games_settings = {'IconPath', 'GamePath', 'ScriptPath'}
    schedule_exists = False
    for k, v in cfg.items():
        if not isinstance(v, dict) and items.get(k) is not None:
            items[k].deserializeFrom(v)

        elif isinstance(v, dict):
            if set(v.keys()) == games_settings:
                self._cfg.addGame(name=k, 
                                  iconPath=v['IconPath'], 
                                  gamePath=v['GamePath'], 
                                  scriptPath=v['ScriptPath'],
                                  save=False
                                  )
            
            else:
                for key, value in v.items():
                    if key == 'Games' and value == 'Schedule':
                        schedule_exists = True
                        continue
                    key = k + "." + key
                    if items.get(key) is not None:
                        items[key].deserializeFrom(value)

    if schedule_exists:
        items['Games.Schedule'].deserializeFrom(cfg['Games']['Schedule'])
    
    self.theme = self.get(self.themeMode)


YEAR = 2023
AUTHOR = "zhiyiYo"
VERSION = __version__
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PySide6/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
ZH_SUPPORT_URL = "https://qfluentwidgets.com/zh/price/"
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load = types.MethodType(customload, qconfig)
qconfig.load('app/config/config.json', cfg)