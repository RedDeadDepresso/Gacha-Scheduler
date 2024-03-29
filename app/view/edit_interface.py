# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

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
            gameConfig.iconPath,
            self.editGroup
        )

        self.gameCard = PushSettingCard(
            self.tr('Browse'),
            FIF.FOLDER,
            self.tr("Game Path"),
            gameConfig.gamePath,
            self.editGroup
        )

        self.scriptCard = PushSettingCard(
            self.tr('Browse'),
            FIF.FOLDER,
            self.tr("Script Path"),
            gameConfig.scriptPath,
            self.editGroup
        )

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
        self.__connectSignalToSlot()

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

    def __onBrowseCardClicked(self, cfgItem):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfgItem) == folder:
            return

        cfg.set(cfgItem, folder)
        self.downloadFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        # music in the pc
        self.iconCard.clicked.connect(
            self.__onBrowseCardClicked)
        pass


