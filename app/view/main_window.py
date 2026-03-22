# coding: utf-8
import ctypes
import ctypes.wintypes
import threading

from PySide6.QtCore import Qt, QSize, Slot, QThreadPool, QObject, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from qfluentwidgets import (Action, NavigationItemPosition, NavigationPushButton, FluentWindow, SplashScreen, qrouter, RoundMenu, SearchLineEdit)
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

    WM_REREGISTER = 0x8001  # Custom message to trigger re-registration
    WM_DISABLE    = 0x8002  # Custom message to unregister hotkey
    WM_ENABLE     = 0x8003  # Custom message to register hotkey

    def __init__(self):
        super().__init__(daemon=True)
        self.signals = HotkeySignals()
        self._hwnd = None

    def _register(self):
        from app.common.config import cfg
        from app.components.shortcut_setting_card import parse_hotkey
        hotkey_str = cfg.get(cfg.hotkey)
        mods, vk = parse_hotkey(hotkey_str)
        ctypes.windll.user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)
        if cfg.get(cfg.hotkeyEnabled):
            ctypes.windll.user32.RegisterHotKey(self._hwnd, HOTKEY_ID, mods, vk)

    def reregister(self):
        if self._hwnd:
            ctypes.windll.user32.PostMessageW(self._hwnd, self.WM_REREGISTER, 0, 0)

    def setEnabled(self, enabled: bool):
        if self._hwnd:
            msg = self.WM_ENABLE if enabled else self.WM_DISABLE
            ctypes.windll.user32.PostMessageW(self._hwnd, msg, 0, 0)

    def run(self):
        user32   = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        HWND_MESSAGE = ctypes.wintypes.HWND(-3)
        self._hwnd = user32.CreateWindowExW(
            0, "STATIC", "GachaHotkeyWindow", 0,
            0, 0, 0, 0,
            HWND_MESSAGE, None, kernel32.GetModuleHandleW(None), None
        )

        if not self._hwnd:
            return

        self._register()

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                ctypes.windll.user32.AllowSetForegroundWindow(
                    ctypes.windll.kernel32.GetCurrentProcessId()
                )
                self.signals.triggered.emit()
            elif msg.message == self.WM_REREGISTER:
                self._register()
            elif msg.message == self.WM_DISABLE:
                user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)
            elif msg.message == self.WM_ENABLE:
                self._register()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)

    def stop(self):
        if self._hwnd:
            ctypes.windll.user32.PostMessageW(self._hwnd, 0x0012, 0, 0)


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

        # Instantiate before connectSignalToSlot so signals can be connected
        self._hotkeyListener = HotkeyListener()
        self._hotkeyListener.start()

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        self.updateManager = UpdateManager(self.threadPool, self)
        self.updateManager.check()

    def initSystemTray(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(self.windowIcon())

        self.trayMenu = RoundMenu(parent=self)
        self.showAction = Action(FIF.VIEW, "Show/Hide")
        self.exitAction = Action(FIF.CLOSE, "Exit")

        self.trayMenu.addAction(self.showAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(self.exitAction)

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.show()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.addGameSignal.connect(self.addGame)
        signalBus.removeGameSignal.connect(self.removeGame)
        signalBus.createThreadSignal.connect(self.createThread)
        signalBus.hotkeyChangedSignal.connect(lambda _: self._hotkeyListener.reregister())
        signalBus.hotkeyEnabledSignal.connect(self._hotkeyListener.setEnabled)
        self._hotkeyListener.signals.triggered.connect(self.toggleVisibility)
        self.showAction.triggered.connect(self.toggleVisibility)

    def initNavigation(self):
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)

        # Search bar added directly to the scroll layout area
        self._searchBox = SearchLineEdit(self.navigationInterface.panel)
        self._searchBox.setPlaceholderText(self.tr('Search games'))
        self._searchBox.setFixedHeight(32)
        self._searchBox.textChanged.connect(self._filterGames)
        self.navigationInterface.panel.scrollLayout.addWidget(self._searchBox)
        self.navigationInterface.panel.scrollLayout.addSpacing(8)

        for gameConfig in cfg.games.values():
            self.addGame(gameConfig)

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

    def _filterGames(self, text: str):
        query = text.strip().lower()
        for gameConfig in cfg.games.values():
            widget = gameConfig.navigationGameWidget
            if widget:
                visible = query == '' or query in gameConfig.name.lower()
                widget.setVisible(visible)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumHeight(500)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('Gacha-Scheduler')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

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

        if hasattr(self, '_searchBox'):
            self._searchBox.clear()

    @Slot(GameConfig)
    def removeGame(self, gameConfig):
        self.stackedWidget.setCurrentWidget(self.scheduleInterface)
        self.navigationInterface.removeWidget(gameConfig.name)
        self.stackedWidget.view.removeWidget(gameConfig.interface)
        if hasattr(self, '_searchBox'):
            self._searchBox.clear()

    @Slot(GameConfig)
    def createThread(self, gameConfig):
        gameRunner = GameRunner(gameConfig)
        self.threadPool.start(gameRunner)