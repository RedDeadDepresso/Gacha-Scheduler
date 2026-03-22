# coding:utf-8
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy

from qfluentwidgets import (BodyLabel, FlyoutAnimationType, Flyout, FlyoutView,
                            PushButton, TransparentToolButton, IconWidget,
                            ImageLabel, ToolTipFilter)
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.components.navigation import NavigationWidget

from ..common.signal_bus import signalBus
from ..common.config import cfg
from ..common.game_runner import GameRunner


class NavigationGameWidget(NavigationWidget):

    def __init__(self, gameConfig, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.gameConfig = gameConfig
        self.name = gameConfig.name

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 8, 4)
        self.layout.setSpacing(8)

        self._addAvatar(gameConfig.iconPath.value)
        self._addNameLabel()
        self.layout.addStretch()
        self._addButtons(gameConfig)

    def _addAvatar(self, iconPath: str):
        if isinstance(iconPath, str) and os.path.exists(iconPath):
            self.avatar = ImageLabel(iconPath)
            self.avatar.setBorderRadius(6, 6, 6, 6)
        else:
            self.avatar = IconWidget(FIF.GAME)
        self.avatar.setFixedSize(32, 32)
        self.layout.addWidget(self.avatar)

    def updateAvatar(self, iconPath: str):
        """Replace the avatar with a new image when the icon path changes."""
        old = self.avatar
        if isinstance(iconPath, str) and os.path.exists(iconPath):
            self.avatar = ImageLabel(iconPath)
            self.avatar.setBorderRadius(6, 6, 6, 6)
        else:
            self.avatar = IconWidget(FIF.GAME)
        self.avatar.setFixedSize(32, 32)
        self.layout.replaceWidget(old, self.avatar)
        old.deleteLater()

    def _addNameLabel(self):
        self.nameLabel = BodyLabel(self.name, self)
        self.nameLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.nameLabel)

    def _addButtons(self, gameConfig):
        self.playButton   = self._makeButton(FIF.PLAY,   'Run game')
        self.scriptButton = self._makeButton(FIF.ROBOT,  'Run with script')
        self.editButton   = self._makeButton(FIF.EDIT,   'Edit')
        self.removeButton = self._makeButton(FIF.DELETE, 'Remove')

        self.playButton.clicked.connect(
            lambda: GameRunner(gameConfig).openProgram(gameConfig.gamePath.value))
        self.scriptButton.clicked.connect(
            lambda: signalBus.createThreadSignal.emit(gameConfig))
        self.removeButton.clicked.connect(self.showRemoveFlyout)

    def _makeButton(self, icon, tooltip: str) -> TransparentToolButton:
        btn = TransparentToolButton(icon, self)
        btn.setFixedSize(28, 28)
        btn.setIconSize(btn.iconSize().__class__(16, 16))
        btn.setToolTip(self.tr(tooltip))
        btn.installEventFilter(ToolTipFilter(btn))
        self.layout.addWidget(btn)
        return btn

    def showRemoveFlyout(self):
        view = FlyoutView(
            title=self.tr('Remove game'),
            content=self.tr('Are you sure you want to remove ') + f'{self.name}?'
        )
        button = PushButton(self.tr('Yes'))
        button.setFixedWidth(120)
        button.clicked.connect(lambda: cfg.removeGame(self.gameConfig))
        button.clicked.connect(view.close)
        view.addWidget(button, align=Qt.AlignLeft)
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.insertSpacing(0, 5)
        view.widgetLayout.addSpacing(5)
        Flyout.make(view, self.removeButton, self.window(),
                    FlyoutAnimationType.SLIDE_RIGHT, isDeleteOnClose=True)