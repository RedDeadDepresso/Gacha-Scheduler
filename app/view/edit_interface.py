# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

from app.common.game_config import GameConfig

from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet


class EditInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, gameConfig, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr(gameConfig.name), self)

        # games
        self.editGroup = SettingCardGroup(
            self.tr('Edit'), self.scrollWidget)

        self.iconCard = PushSettingCard(
            self.tr('Browse'),
            FIF.FOLDER,
            self.tr("Icon Path"),
            cfg.get(gameConfig.iconPath),
            self.editGroup
        )

        self.gameCard = PushSettingCard(
            self.tr('Browse'),
            FIF.FOLDER,
            self.tr("Game Path"),
            cfg.get(gameConfig.gamePath),
            self.editGroup
        )

        self.scriptCard = PushSettingCard(
            self.tr('Browse'),
            FIF.FOLDER,
            self.tr("Script Path"),
            cfg.get(gameConfig.scriptPath),
            self.editGroup
        )

        self.iconCard.clicked.connect(
            lambda item=gameConfig.iconPath, card=self.iconCard: self.openImageDialog(item, card))

        self.scriptCard.clicked.connect(
            lambda item=gameConfig.scriptPath, card=self.scriptCard: self.openExeDialog(item, card))
        
        self.gameCard.clicked.connect(
            lambda item=gameConfig.gamePath, card=self.gameCard: self.openExeDialog(item, card))
        
        self.__initWidget()


    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('editInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.editGroup.addSettingCard(self.iconCard)
        self.editGroup.addSettingCard(self.gameCard)
        self.editGroup.addSettingCard(self.scriptCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.editGroup)

    @Slot(GameConfig, PushSettingCard)
    def openImageDialog(self, item, card):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Add Icon", "", "Images (*.png *.xpm *.jpg)", options=options)
        if not fileName or cfg.get(item) == fileName:
            return
        
        cfg.set(item, fileName)
        card.setContent(fileName)

    @Slot(GameConfig, PushSettingCard)
    def openExeDialog(self, item, card):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Add Executable", "", "Executable Files (*.exe *.py)", options=options)
        if not fileName or cfg.get(item) == fileName:
            return
        
        cfg.set(item, fileName)
        card.setContent(fileName)



