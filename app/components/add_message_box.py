# coding:utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QFileDialog

from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PushButton, setTheme, Theme


class AddMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr('Add Game'), self)
        self.nameLineEdit = LineEdit(self)

        # Create two QHBoxLayouts, each containing a LineEdit and a PushButton
        self.gameLayout = QHBoxLayout()
        self.gameLineEdit = LineEdit(self)
        self.gameDialogButton = PushButton(self.tr('Browse'), self)
        self.gameLayout.addWidget(self.gameLineEdit)
        self.gameLayout.addWidget(self.gameDialogButton)

        self.scriptLayout = QHBoxLayout()
        self.scriptLineEdit = LineEdit(self)
        self.scriptDialogButton = PushButton(self.tr('Browse'), self)
        self.scriptLayout.addWidget(self.scriptLineEdit)
        self.scriptLayout.addWidget(self.scriptDialogButton)

        self.nameLineEdit.setPlaceholderText(self.tr('Enter name of the game'))
        self.gameLineEdit.setPlaceholderText(self.tr('Enter game path'))
        self.scriptLineEdit.setPlaceholderText(self.tr('Enter script path'))

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameLineEdit)
        self.viewLayout.addLayout(self.gameLayout)
        self.viewLayout.addLayout(self.scriptLayout)

        # change the text of button
        self.yesButton.setText(self.tr('Save'))
        self.cancelButton.setText(self.tr('Cancel'))

        self.widget.setMinimumWidth(500)

        # connect the file dialog buttons to methods
        self.gameDialogButton.clicked.connect(self.openGameDialog)
        self.scriptDialogButton.clicked.connect(self.openScriptDialog)

    def openGameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)
        if fileName:
            self.gameLineEdit.setText(fileName)  # update the first LineEdit with the selected file

    def openScriptDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)
        if fileName:
            self.scriptLineEdit.setText(fileName)  # update the second LineEdit with the selected file


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        # self.setStyleSheet('Demo{background:rgb(32,32,32)}')

        self.hBxoLayout = QHBoxLayout(self)
        self.button = PushButton('Test', self)

        self.resize(600, 600)
        self.hBxoLayout.addWidget(self.button, 0, Qt.AlignCenter)
        self.button.clicked.connect(self.showDialog)

    def showDialog(self):
        w = AddMessageBox(self)
        if w.exec():
            print(w.nameLineEdit.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()