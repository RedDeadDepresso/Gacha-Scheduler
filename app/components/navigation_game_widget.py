# coding:utf-8
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from qfluentwidgets import BodyLabel, FlyoutAnimationType, Flyout, FlyoutView, PushButton, ToolButton, IconWidget, ImageLabel
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.components.navigation import NavigationWidget

from ..common.signal_bus import signalBus
from ..common.config import cfg
from ..common.game_runner import GameRunner


class NavigationGameWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, gameConfig, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.gameConfig = gameConfig
        self.name = gameConfig.name
        self.layout = QHBoxLayout(self)

        self.setAvatar(gameConfig.iconPath.value)
        self.setNameLabel()

        self.playButton = self.setToolButton(FIF.PLAY, 'Run')
        self.scriptButton = self.setToolButton(FIF.ROBOT, 'Run with Script')
        self.editButton = self.setToolButton(FIF.EDIT, 'Edit')
        self.removeButton = self.setToolButton(FIF.DELETE, 'Remove')

        self.__connectSignalToSlot(gameConfig)

    def setNameLabel(self):
        self.nameLabel = BodyLabel(self.name, self)
        self.layout.addWidget(self.nameLabel)

    def setAvatar(self, avatar: str | None):
        if isinstance(avatar, str) and os.path.exists(avatar):
            self.avatar = ImageLabel(avatar)
            self.avatar.setBorderRadius(8, 8, 8, 8)
        else:
            self.avatar = IconWidget(FIF.GAME)
            
        self.avatar.setFixedSize(28, 28)
        self.layout.addWidget(self.avatar)

    def setToolButton(self, fluentIcon: FIF, toolTip: str):
        toolButton = ToolButton(fluentIcon, self)
        toolButton.setToolTip(self.tr(toolTip))
        toolButton.setFixedSize(28, 28)
        self.layout.addWidget(toolButton)
        return toolButton

    def showRemoveFlyout(self):
        view = FlyoutView(
            title=self.tr('Warning'),
            content=self.tr("Are you sure you want to remove ") + f"{self.name}?"
        )
        # add button to view
        button = PushButton(self.tr('Yes'))
        button.setFixedWidth(120)
        button.clicked.connect(lambda: cfg.removeGame(self.gameConfig))
        button.clicked.connect(view.close)
        view.addWidget(button, align=Qt.AlignLeft)

        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.insertSpacing(0, 5)
        view.widgetLayout.addSpacing(5)

        # show view
        Flyout.make(view, self.removeButton, self.window(), FlyoutAnimationType.SLIDE_RIGHT, isDeleteOnClose=True)

    def __connectSignalToSlot(self, gameConfig):
        self.playButton.clicked.connect(lambda: GameRunner(gameConfig).openProgram(gameConfig.gamePath.value))
        self.scriptButton.clicked.connect(lambda: signalBus.createThreadSignal.emit(gameConfig))
        self.removeButton.clicked.connect(self.showRemoveFlyout)
        
