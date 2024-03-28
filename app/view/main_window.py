# coding: utf-8
from typing import List
from PySide6.QtCore import Qt, Signal, QEasingCurve, QUrl, QSize
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, NavigationPushButton, MessageBox, FluentWindow,
                            SplashScreen)
from qfluentwidgets import FluentIcon as FIF

from .schedule_interface import ScheduleInterface
from .setting_interface import SettingInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource
from ..components.add_message_box import AddMessageBox
from ..components.navigation_game_widget import NavigationGameWidget


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.scheduleInterface = ScheduleInterface(self)
        self.settingInterface = SettingInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.setCollapsible(False)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)

        pos = NavigationItemPosition.SCROLL
        self.navigationInterface.addWidget(
            'game', 
            NavigationGameWidget('Arknights', 'app/resource/images/arknights.png'),
            None,
            pos
        )

        # add custom widget to bottom
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            'AddGame',
            NavigationPushButton(FIF.ADD, self.tr('Add Game'), False),
            self.showMessageBox,
            NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.scheduleInterface, FIF.DATE_TIME, self.tr('Schedule'), NavigationItemPosition.BOTTOM)
        
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('Gacha-Scheduler')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def showMessageBox(self):
        w = AddMessageBox(self)
        w.exec()