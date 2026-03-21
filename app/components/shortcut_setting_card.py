# coding: utf-8
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QKeyEvent, QIcon
from PySide6.QtWidgets import QHBoxLayout, QPushButton
from qfluentwidgets import (SettingCard, FluentIconBase, FluentIcon,
                            MessageBoxBase, SubtitleLabel, CaptionLabel,
                            PushButton, TransparentToolButton)
from typing import Union

from ..common.config import cfg
from ..common.signal_bus import signalBus


# Map Qt key codes to Win32 virtual key codes
_VK_MAP = {
    Qt.Key.Key_A: 0x41, Qt.Key.Key_B: 0x42, Qt.Key.Key_C: 0x43,
    Qt.Key.Key_D: 0x44, Qt.Key.Key_E: 0x45, Qt.Key.Key_F: 0x46,
    Qt.Key.Key_G: 0x47, Qt.Key.Key_H: 0x48, Qt.Key.Key_I: 0x49,
    Qt.Key.Key_J: 0x4A, Qt.Key.Key_K: 0x4B, Qt.Key.Key_L: 0x4C,
    Qt.Key.Key_M: 0x4D, Qt.Key.Key_N: 0x4E, Qt.Key.Key_O: 0x4F,
    Qt.Key.Key_P: 0x50, Qt.Key.Key_Q: 0x51, Qt.Key.Key_R: 0x52,
    Qt.Key.Key_S: 0x53, Qt.Key.Key_T: 0x54, Qt.Key.Key_U: 0x55,
    Qt.Key.Key_V: 0x56, Qt.Key.Key_W: 0x57, Qt.Key.Key_X: 0x58,
    Qt.Key.Key_Y: 0x59, Qt.Key.Key_Z: 0x5A,
    Qt.Key.Key_0: 0x30, Qt.Key.Key_1: 0x31, Qt.Key.Key_2: 0x32,
    Qt.Key.Key_3: 0x33, Qt.Key.Key_4: 0x34, Qt.Key.Key_5: 0x35,
    Qt.Key.Key_6: 0x36, Qt.Key.Key_7: 0x37, Qt.Key.Key_8: 0x38,
    Qt.Key.Key_9: 0x39,
    Qt.Key.Key_F1:  0x70, Qt.Key.Key_F2:  0x71, Qt.Key.Key_F3:  0x72,
    Qt.Key.Key_F4:  0x73, Qt.Key.Key_F5:  0x74, Qt.Key.Key_F6:  0x75,
    Qt.Key.Key_F7:  0x76, Qt.Key.Key_F8:  0x77, Qt.Key.Key_F9:  0x78,
    Qt.Key.Key_F10: 0x79, Qt.Key.Key_F11: 0x7A, Qt.Key.Key_F12: 0x7B,
    Qt.Key.Key_Space:     0x20, Qt.Key.Key_Return:    0x0D,
    Qt.Key.Key_Escape:    0x1B, Qt.Key.Key_Tab:       0x09,
    Qt.Key.Key_Backspace: 0x08, Qt.Key.Key_Delete:    0x2E,
    Qt.Key.Key_Insert:    0x2D, Qt.Key.Key_Home:      0x24,
    Qt.Key.Key_End:       0x23, Qt.Key.Key_PageUp:    0x21,
    Qt.Key.Key_PageDown:  0x22, Qt.Key.Key_Left:      0x25,
    Qt.Key.Key_Up:        0x26, Qt.Key.Key_Right:     0x27,
    Qt.Key.Key_Down:      0x28,
}

_MOD_NAMES = {"ctrl": 0x0002, "alt": 0x0001, "shift": 0x0004, "win": 0x0008}


def parse_hotkey(hotkey_str: str) -> tuple[int, int]:
    """Parse 'Ctrl+Alt+H' into (win32_mods, vk) for RegisterHotKey."""
    parts = [p.strip() for p in hotkey_str.split("+")]
    mods = 0
    vk = 0
    for part in parts:
        lower = part.lower()
        if lower in _MOD_NAMES:
            mods |= _MOD_NAMES[lower]
        else:
            for qt_key, vk_code in _VK_MAP.items():
                if QKeySequence(qt_key).toString().upper() == part.upper():
                    vk = vk_code
                    break
    return mods, vk


class KeyCaptureDialog(MessageBoxBase):
    """Dialog that captures a full key combination including multiple modifiers."""

    DEFAULT_HOTKEY = "Ctrl+Alt+H"

    def __init__(self, current: str, parent=None):
        super().__init__(parent)
        self._pending = current

        self.titleLabel = SubtitleLabel("Activate shortcut key", self)
        self.hintLabel  = CaptionLabel(
            "Press a combination of keys to change this shortcut key", self)

        self._badgeContainer = QHBoxLayout()
        self._badgeContainer.setSpacing(6)
        self._badgeContainer.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.hintLabel)
        self.viewLayout.addSpacing(20)
        self.viewLayout.addLayout(self._badgeContainer)
        self.viewLayout.addSpacing(20)

        self.yesButton.setText("OK")
        self.cancelButton.setText("Cancel")

        self.resetButton = PushButton("Reset", self)
        self.resetButton.clicked.connect(self._onReset)
        self.buttonLayout.insertWidget(1, self.resetButton)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        self._renderBadges(current)

    def _renderBadges(self, hotkey: str):
        while self._badgeContainer.count():
            item = self._badgeContainer.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for part in hotkey.split("+"):
            badge = _DialogKeyBadge(part.strip())
            self._badgeContainer.addWidget(badge)
        self._badgeContainer.addStretch()

    def keyPressEvent(self, event: QKeyEvent):
        key  = event.key()
        mods = event.modifiers()

        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift,
                   Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
            return

        parts = []
        if mods & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if mods & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        if mods & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if mods & Qt.KeyboardModifier.MetaModifier:
            parts.append("Win")

        key_str = QKeySequence(key).toString()
        if key_str:
            parts.append(key_str)

        if parts:
            self._pending = "+".join(parts)
            self._renderBadges(self._pending)

    def _onReset(self):
        self._pending = self.DEFAULT_HOTKEY
        self._renderBadges(self._pending)

    def getValue(self) -> str:
        return self._pending


class _DialogKeyBadge(QPushButton):
    """Large key badge shown inside the capture dialog."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "QPushButton {"
            "  background: #00D4D4; color: #000; border-radius: 8px;"
            "  padding: 18px 24px; font-size: 18px; font-weight: bold;"
            "  border: none;"
            "}"
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


class KeyBadge(QPushButton):
    """Small key badge shown on the setting card."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "QPushButton {"
            "  background: #00D4D4; color: #000; border-radius: 6px;"
            "  padding: 4px 10px; font-weight: bold; font-size: 13px;"
            "  border: none;"
            "}"
        )
        self.setFixedHeight(32)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


class ShortcutSettingCard(SettingCard):
    """Setting card that displays the current hotkey as badges and opens a picker."""

    shortcutChanged = Signal(str)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase],
                 title: str, content: str = None, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        self._badgeLayout = QHBoxLayout()
        self._badgeLayout.setSpacing(4)
        self._badgeLayout.setContentsMargins(0, 0, 0, 0)

        self.editButton = TransparentToolButton(FluentIcon.EDIT, self)
        self.editButton.setFixedSize(32, 32)
        self.editButton.clicked.connect(self._openPicker)

        self.hBoxLayout.addLayout(self._badgeLayout)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.editButton)
        self.hBoxLayout.addSpacing(16)

        self._renderBadges(cfg.get(configItem))

    def _renderBadges(self, hotkey: str):
        while self._badgeLayout.count():
            item = self._badgeLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for part in hotkey.split("+"):
            badge = KeyBadge(part.strip(), self)
            self._badgeLayout.addWidget(badge)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.editButton.setEnabled(enabled)

    def _openPicker(self):
        current = cfg.get(self.configItem)
        dialog = KeyCaptureDialog(current, self.window())
        if dialog.exec():
            new_hotkey = dialog.getValue()
            if new_hotkey and new_hotkey != current:
                cfg.set(self.configItem, new_hotkey)
                self._renderBadges(new_hotkey)
                self.shortcutChanged.emit(new_hotkey)
                signalBus.hotkeyChangedSignal.emit(new_hotkey)