# coding: utf-8
from PySide6.QtCore import Qt, Signal, QSize, Slot, QThreadPool
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from pynput import keyboard

from qfluentwidgets import (Action, NavigationItemPosition, NavigationPushButton, FluentWindow, SplashScreen, qrouter, RoundMenu)
from qfluentwidgets import FluentIcon as FIF

from .edit_interface import EditInterface
from .schedule_interface import ScheduleInterface
from .setting_interface import SettingInterface
from ..common.config import cfg
from ..common.game_config import GameConfig
from ..common.game_runner import GameRunner
from ..common.signal_bus import signalBus
from ..common import resource
from ..components.add_message_box import AddMessageBox
from ..components.navigation_game_widget import NavigationGameWidget


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.threadPool = QThreadPool() 

        # create sub interface
        self.scheduleInterface = ScheduleInterface(self)
        self.settingInterface = SettingInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.setCollapsible(False)

        self.initSystemTray()
        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()
        keyboard.GlobalHotKeys({'<ctrl>+<alt>+h': signalBus.toggleVisibilitySignal.emit}).start()

    def initSystemTray(self):
        # Create a QSystemTrayIcon
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(self.windowIcon())
        
        # Create a QMenu
        self.trayMenu = RoundMenu(parent=self)
        self.showAction = Action(FIF.VIEW, "Show/Hide")
        self.exitAction = Action(FIF.CLOSE, "Exit")

        self.trayMenu.addAction(self.showAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(self.exitAction)

        # Set the context menu for the tray icon to the created menu
        self.trayIcon.setContextMenu(self.trayMenu)

        # Show the tray icon
        self.trayIcon.show()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.addGameSignal.connect(self.addGame)
        signalBus.removeGameSignal.connect(self.removeGame)
        signalBus.createThreadSignal.connect(self.createThread)
        signalBus.toggleVisibilitySignal.connect(self.toggleVisibility)
        self.showAction.triggered.connect(self.toggleVisibility)

    def initNavigation(self):
        # add navigation items
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)

        for gameConfig in cfg.games.values():
            self.addGame(gameConfig)

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
        
        self.stackedWidget.setCurrentWidget(self.scheduleInterface, False)
        
    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumHeight(500)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('Gacha Scheduler')

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

    def closeEvent(self, event):
        if self.trayIcon is not None:
            event.ignore()
            self.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def toggleVisibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def showMessageBox(self):
        w = AddMessageBox(self)
        w.exec()

    @Slot(GameConfig)
    def addGame(self, gameConfig):
        interface = EditInterface(gameConfig, self)
        interface.setProperty("isStackedTransparent", False)
        self.stackedWidget.addWidget(interface)
    
        widget = NavigationGameWidget(gameConfig)    
        self.navigationInterface.addWidget(
            gameConfig.name, 
            widget,
            None,
            NavigationItemPosition.SCROLL
        )
        self.navigationInterface.panel.scrollLayout.addSpacing(3)
        widget.editButton.clicked.connect(lambda checked=False, interface=interface: self.switchTo(interface))
        gameConfig.interface = interface
        gameConfig.navigationGameWidget = widget

    @Slot(GameConfig)
    def removeGame(self, gameConfig):
        self.stackedWidget.setCurrentWidget(self.scheduleInterface)
        self.navigationInterface.removeWidget(gameConfig.name)
        self.stackedWidget.view.removeWidget(gameConfig.interface)

    @Slot(GameConfig)
    def createThread(self, gameConfig):
        gameRunner = GameRunner(gameConfig)
        self.threadPool.start(gameRunner)
    