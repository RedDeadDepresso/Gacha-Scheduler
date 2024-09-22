# coding:utf-8
from qfluentwidgets import SettingCardGroup, PushSettingCard, ScrollArea, ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

from app.common.game_config import GameConfig
from ..common.config import cfg
from ..common.style_sheet import StyleSheet
from ..components.file_setting_card import FileType, FileSettingCard


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
            self.tr(''), self.scrollWidget)

        self.iconCard = FileSettingCard(
            FileType.IMAGE, 
            gameConfig.iconPath, 
            FIF.PHOTO, 
            self.tr("Icon Path"),
            parent=self.editGroup
        )
        self.gameCard = FileSettingCard(
            FileType.EXE,
            gameConfig.gamePath, 
            FIF.GAME, 
            self.tr("Game Path"), 
            parent=self.editGroup
        )
        self.scriptCard = FileSettingCard(
            FileType.EXE, 
            gameConfig.scriptPath,
            FIF.ROBOT, 
            self.tr("Script Path"),
            parent=self.editGroup
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

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.editGroup.addSettingCard(self.iconCard)
        self.editGroup.addSettingCard(self.gameCard)
        self.editGroup.addSettingCard(self.scriptCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 0, 36, 0)
        self.expandLayout.addWidget(self.editGroup)



