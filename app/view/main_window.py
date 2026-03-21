# coding: utf-8
import ctypes
import ctypes.wintypes
import threading

from PySide6.QtCore import Qt, QSize, Slot, QThreadPool, QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from qfluentwidgets import (Action, NavigationItemPosition, NavigationPushButton, FluentWindow, SplashScreen, qrouter, RoundMenu)
from qfluentwidgets import FluentIcon as FIF

from .edit_interface import EditInterface
from .schedule_interface import ScheduleInterface
from .setting_interface import SettingInterface
from ..common.config import cfg
from ..common.game_config import GameConfig
from ..common.game_runner import GameRunner
from ..common.signal_bus import signalBus
from ..common.updater import UpdateManager
from ..common import resource
from ..components.add_message_box import AddMessageBox
from ..components.navigation_game_widget import NavigationGameWidget

MOD_CONTROL = 0x0002
MOD_ALT     = 0x0001
HOTKEY_ID   = 1
WM_HOTKEY   = 0x0312
VK_H        = 0x48
PM_REMOVE   = 0x0001


class HotkeySignals(QObject):
    triggered = Signal()


class HotkeyListener(threading.Thread):
    """
    Runs a Win32 message loop on its own thread with a message-only window.
    Message-only windows (HWND_MESSAGE) receive WM_HOTKEY even when hidden,
    and since RegisterHotKey is called on this thread Windows delivers the
    message here — giving us full foreground focus permission.
    """

    def __init__(self):
        super().__init__(daemon=True)
        self.signals = HotkeySignals()
        self._hwnd = None

    def run(self):
        user32   = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        # Create a message-only window (invisible, no taskbar entry)
        HWND_MESSAGE = ctypes.wintypes.HWND(-3)
        wc = ctypes.wintypes.WNDCLASS if hasattr(ctypes.wintypes, 'WNDCLASS') else None

        # Use CreateWindowEx directly with a pre-registered class (static control)
        self._hwnd = user32.CreateWindowExW(
            0, "STATIC", "GachaHotkeyWindow", 0,
            0, 0, 0, 0,
            HWND_MESSAGE, None, kernel32.GetModuleHandleW(None), None
        )

        if not self._hwnd:
            return

        user32.RegisterHotKey(self._hwnd, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_H)

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                # Call SetForegroundWindow HERE, on this thread, while we still
                # have foreground permission from receiving the input event.
                # We don't have the main window's hwnd here so we emit a signal
                # first to show() the window, then steal focus via AllowSetForegroundWindow
                ctypes.windll.user32.AllowSetForegroundWindow(
                    ctypes.windll.kernel32.GetCurrentProcessId()
                )
                self.signals.triggered.emit()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)

    def stop(self):
        if self._hwnd:
            ctypes.windll.user32.PostMessageW(self._hwnd, 0x0012, 0, 0)  # WM_QUIT


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

        # Start hotkey listener on its own message-loop thread
        self._hotkeyListener = HotkeyListener()
        self._hotkeyListener.signals.triggered.connect(self.toggleVisibility)
        self._hotkeyListener.start()

        self.updateManager = UpdateManager(self.threadPool, self)
        self.updateManager.check()

    def initSystemTray(self):
        # Create a QSystemTrayIcon
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(self.windowIcon())

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

    def closeEvent(self, event):
        if self.trayIcon is not None:
            event.ignore()
            self.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def toggleVisibility(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal()
            self.raise_()
            ctypes.windll.user32.SetForegroundWindow(int(self.winId()))

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