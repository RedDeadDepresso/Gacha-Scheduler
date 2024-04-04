# coding:utf-8
import os
import subprocess
from typing import Union, List

from PySide6.QtCore import (Qt, Signal, QRect, QRectF, QPropertyAnimation, Property, QMargins,
                          QEasingCurve, QPoint, QEvent, QSize)
from PySide6.QtGui import QColor, QPainter, QPen, QIcon, QCursor, QFont, QBrush, QPixmap, QImage
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget
from collections import deque

from qfluentwidgets import BodyLabel, FlyoutAnimationType, Flyout, FlyoutView, PushButton, ToolButton
from qfluentwidgets.common.config import isDarkTheme
from qfluentwidgets.common.style_sheet import themeColor
from qfluentwidgets.common.icon import drawIcon, toQIcon
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.common.font import setFont
from qfluentwidgets.components.navigation import NavigationAvatarWidget, NavigationWidget

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
        self.setAvatarLabel(gameConfig.iconPath.value)
        self.setNameLabel()
        self.setPlayButton()
        self.setScriptButton()
        self.setEditButton()
        self.setRemoveButton()
        self.__connectSignalToSlot(gameConfig)

    def setNameLabel(self):
        self.nameLabel = BodyLabel(self.name, self)
        self.layout.addWidget(self.nameLabel)

    def setAvatarLabel(self, avatar: Union[str, QPixmap, QImage]):
        valid = False
        if isinstance(avatar, QPixmap):
            avatar = avatar.toImage()
            valid = True
        elif isinstance(avatar, str) and os.path.exists(avatar):
            avatar = QImage(avatar)
            if not avatar.isNull():
                valid = True
                
        if not valid:
            avatar = QImage(FIF.GAME.path())

        self.avatar = avatar.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.avatarLabel = QLabel(self)
        self.avatarLabel.setPixmap(QPixmap.fromImage(self.avatar))
        self.layout.addWidget(self.avatarLabel)

    def setPlayButton(self):
        self.playButton = ToolButton(FIF.PLAY_SOLID, self)
        self.playButton.setToolTip(self.tr('Run'))
        self.layout.addWidget(self.playButton)

    def setScriptButton(self):
        self.scriptButton = ToolButton(FIF.ROBOT, self)
        self.scriptButton.setToolTip(self.tr('Run with script'))
        self.layout.addWidget(self.scriptButton)

    def setEditButton(self):
        self.editButton = ToolButton(FIF.EDIT, self)
        self.editButton.setToolTip(self.tr('Edit'))
        self.layout.addWidget(self.editButton)

    def setRemoveButton(self):
        self.removeButton = ToolButton(FIF.DELETE, self)
        self.removeButton.setToolTip(self.tr('Remove'))
        self.layout.addWidget(self.removeButton)

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

        # adjust layout (optional)
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.insertSpacing(0, 5)
        view.widgetLayout.addSpacing(5)

        # show view
        Flyout.make(view, self.removeButton, self.window(), FlyoutAnimationType.SLIDE_RIGHT, isDeleteOnClose=True)

    def __connectSignalToSlot(self, gameConfig):
        self.playButton.clicked.connect(lambda: GameRunner(gameConfig).openProgram(gameConfig.gamePath.value))
        self.scriptButton.clicked.connect(lambda: signalBus.createThreadSignal.emit(gameConfig))
        self.removeButton.clicked.connect(self.showRemoveFlyout)
        
