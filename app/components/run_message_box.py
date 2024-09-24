from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import Dialog, AvatarWidget, BodyLabel, SubtitleLabel, FluentTitleBar
from app.common.signal_bus import signalBus

class RunMessageBox(Dialog):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, gameConfig, parent=None):
        self.gameConfig = gameConfig
        if gameConfig.iconPath.value:
            super().__init__('Gacha Scheduler', '', parent)
            self.layoutWithIcon()
            self.setWindowIcon(QIcon(gameConfig.iconPath.value))
        else:
            super().__init__('Gacha Scheduler', f'Do you want to run {gameConfig.name}?')
            self.titleLabel.setText("Arknights")
        self.__connectSignalToSlot()
        self.setWindowTitle(f"{gameConfig.name} - Gacha Scheduler")
        self.setTitleBar(FluentTitleBar(self))

    def layoutWithIcon(self):
        self.headerLayout = QHBoxLayout()
        self.avatarLayout = QHBoxLayout()
        self.contentLayout = QVBoxLayout()

        self.avatarLayout.setContentsMargins(24, 24, 0, 0)
        self.avatarLayout.addWidget(AvatarWidget(self.gameConfig.iconPath.value))

        self.contentLayout.setSpacing(12)
        self.contentLayout.setContentsMargins(24, 24, 24, 24)
        self.contentLayout.addWidget(SubtitleLabel(self.gameConfig.name), 0, Qt.AlignTop)
        self.contentLayout.addWidget(BodyLabel(f"Do you want to run {self.gameConfig.name}?"), 0, Qt.AlignTop)

        self.headerLayout.addLayout(self.avatarLayout)
        self.headerLayout.addLayout(self.contentLayout)
        self.vBoxLayout.insertLayout(1, self.headerLayout)

        self.textLayout.removeWidget(self.titleLabel)
        self.textLayout.removeWidget(self.contentLabel)

    def runGame(self):
        signalBus.createThreadSignal.emit(self.gameConfig)

    def __connectSignalToSlot(self):
        self.yesButton.clicked.connect(self.runGame)
