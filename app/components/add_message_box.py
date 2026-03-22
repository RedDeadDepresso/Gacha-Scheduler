# coding:utf-8
import os

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtCore import Qt, QTimer
from qfluentwidgets import (MessageBoxBase, SubtitleLabel, BodyLabel,
                            CaptionLabel, LineEdit, PushButton)
from ..common.config import cfg
from ..components.file_setting_card import _executable_filter, _executable_extensions


class FieldLayout(QVBoxLayout):
    """Label + input row + fixed-height error caption."""

    ERROR_HEIGHT = 16  # reserved space so layout doesn't jump on error

    def __init__(self, label: str, lineEdit: LineEdit,
                 browseButton: PushButton = None, parent=None):
        super().__init__()
        self.lineEdit = lineEdit
        self.setSpacing(3)

        self.titleLabel = BodyLabel(label, parent)

        inputRow = QHBoxLayout()
        inputRow.setSpacing(8)
        inputRow.addWidget(lineEdit)
        if browseButton:
            inputRow.addWidget(browseButton)

        self.errorLabel = CaptionLabel("", parent)
        self.errorLabel.setStyleSheet(f"color: #e05c5c;")
        self.errorLabel.setFixedHeight(self.ERROR_HEIGHT)

        self.addWidget(self.titleLabel)
        self.addLayout(inputRow)
        self.addWidget(self.errorLabel)

    def setError(self, message: str):
        if message:
            self.lineEdit.setError(True)
            self.lineEdit.setStyleSheet("border: 1px solid #e05c5c;")
            self.errorLabel.setText(message)
        else:
            self.lineEdit.setError(False)
            self.lineEdit.setStyleSheet("")
            self.errorLabel.setText("")


class AddMessageBox(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Add Game'), self)

        self.nameLineEdit   = LineEdit(self)
        self.iconLineEdit   = LineEdit(self)
        self.gameLineEdit   = LineEdit(self)
        self.scriptLineEdit = LineEdit(self)

        self.iconDialogButton   = PushButton(self.tr('Browse'), self)
        self.gameDialogButton   = PushButton(self.tr('Browse'), self)
        self.scriptDialogButton = PushButton(self.tr('Browse'), self)

        self.nameField   = FieldLayout(self.tr('Name *'),       self.nameLineEdit,   parent=self)
        self.iconField   = FieldLayout(self.tr('Icon'),         self.iconLineEdit,   self.iconDialogButton,   self)
        self.gameField   = FieldLayout(self.tr('Game path *'),  self.gameLineEdit,   self.gameDialogButton,   self)
        self.scriptField = FieldLayout(self.tr('Script path'),  self.scriptLineEdit, self.scriptDialogButton, self)

        self.nameLineEdit.setPlaceholderText(self.tr('Enter game name'))
        self.iconLineEdit.setPlaceholderText(self.tr('Enter icon path'))
        self.gameLineEdit.setPlaceholderText(self.tr('Enter game path'))
        self.scriptLineEdit.setPlaceholderText(self.tr('Enter script path'))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(8)
        self.viewLayout.addLayout(self.nameField)
        self.viewLayout.addLayout(self.iconField)
        self.viewLayout.addLayout(self.gameField)
        self.viewLayout.addLayout(self.scriptField)

        self.yesButton.setText(self.tr('Save'))
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.setText(self.tr('Cancel'))
        self.widget.setMinimumWidth(560)

        self.iconDialogButton.clicked.connect(lambda: self._browseImage(self.iconLineEdit))
        self.gameDialogButton.clicked.connect(lambda: self._browseExe(self.gameLineEdit))
        self.scriptDialogButton.clicked.connect(lambda: self._browseExe(self.scriptLineEdit))

        # Debounce timer for name (duplicate check feels jarring on every keystroke)
        self._nameTimer = QTimer(self)
        self._nameTimer.setSingleShot(True)
        self._nameTimer.setInterval(400)
        self._nameTimer.timeout.connect(self._validateName)

        # Name: debounced duplicate check on typing, required check on leave
        self.nameLineEdit.textChanged.connect(self._onNameChanged)
        self.nameLineEdit.editingFinished.connect(self._validateName)

        # Paths: validate immediately on typing
        self.iconLineEdit.textChanged.connect(lambda t: self._validatePath(t, self.iconField, required=False, extensions=self.IMAGE_EXTENSIONS))
        self.gameLineEdit.textChanged.connect(lambda t: self._validatePath(t, self.gameField, required=True, extensions=self.EXE_EXTENSIONS))
        self.scriptLineEdit.textChanged.connect(lambda t: self._validatePath(t, self.scriptField, required=False, extensions=self.EXE_EXTENSIONS))

    @property
    def name(self):
        return self.nameLineEdit.text().strip()

    @property
    def iconPath(self):
        return self.iconLineEdit.text().strip()

    @property
    def gamePath(self):
        return self.gameLineEdit.text().strip()

    @property
    def scriptPath(self):
        return self.scriptLineEdit.text().strip()

    def _onNameChanged(self, text):
        # Clear error immediately when user starts typing again
        if not text.strip():
            self.nameField.setError("")
        else:
            self._nameTimer.start()

    def _validateName(self) -> bool:
        name = self.name
        if not name:
            # Only show "required" if the field has been touched and left
            if not self.nameLineEdit.text():
                self.nameField.setError("")  # silent until submit
            return False
        if cfg.getGame(name) is not None:
            self.nameField.setError(self.tr("A game with this name already exists"))
            return False
        self.nameField.setError("")
        return True

    IMAGE_EXTENSIONS = {'.png', '.xpm', '.jpg', '.jpeg', '.webp'}
    EXE_EXTENSIONS   = _executable_extensions()

    def _validatePath(self, text: str, field: FieldLayout, required: bool,
                      extensions: set = None) -> bool:
        text = text.strip()
        if not text:
            if required and self.gameLineEdit.text():
                field.setError(self.tr("This field is required"))
                return False
            field.setError("")
            return not required
        if not os.path.exists(text):
            field.setError(self.tr("File not found"))
            return False
        if extensions and os.path.splitext(text)[1].lower() not in extensions:
            field.setError(self.tr("Invalid file type"))
            return False
        field.setError("")
        return True

    def _validate(self) -> bool:
        valid = True

        name = self.name
        if not name:
            self.nameField.setError(self.tr("Name is required"))
            valid = False
        elif cfg.getGame(name) is not None:
            self.nameField.setError(self.tr("A game with this name already exists"))
            valid = False
        else:
            self.nameField.setError("")

        if not self._validatePath(self.iconPath, self.iconField, required=False, extensions=self.IMAGE_EXTENSIONS):
            valid = False
        if not self._validatePath(self.gamePath, self.gameField, required=True, extensions=self.EXE_EXTENSIONS):
            valid = False
        if not self._validatePath(self.scriptPath, self.scriptField, required=False, extensions=self.EXE_EXTENSIONS):
            valid = False

        return valid

    def _browseImage(self, lineEdit):
        fileName, _ = QFileDialog.getOpenFileName(
            self, self.tr("Add Icon"), "", "Images (*.png *.xpm *.jpg *.webp)")
        if fileName:
            lineEdit.setText(fileName)

    def _browseExe(self, lineEdit):
        fileName, _ = QFileDialog.getOpenFileName(
            self, self.tr("Add Executable"), "",
            _executable_filter(),
            options=QFileDialog.Option.DontResolveSymlinks)
        if fileName:
            lineEdit.setText(fileName)

    def __onYesButtonClicked(self):
        if self._validate():
            cfg.addGame(self.name, self.iconPath, self.gamePath, self.scriptPath)
            self.accept()
            self.accepted.emit()