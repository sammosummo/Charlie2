"""Widget for backing up data to Google Drive.

"""
from pickle import load
from logging import getLogger
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QEventLoop
from httplib2 import ServerNotFoundError
from charlie2.tools.googledrive import backup
from charlie2.tools.paths import last_backed_up


logger = getLogger(__name__)


class BackupWidget(QWidget):
    def __init__(self, parent=None):
        super(BackupWidget, self).__init__(parent=parent)
        logger.info(f"initialised {type(self)}")

        # instructions
        self.instructions = self.parent().instructions

        # layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # layout > last backed up message
        self.label = QLabel(self.instructions[52] % self._last_backed_up)
        self.layout.addWidget(self.label)

        # layout > backup button
        self.button = QPushButton(self.instructions[53])
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self._attempt_backup)

        # layout > stretch factor
        self.layout.addStretch(1)

    @property
    def _last_backed_up(self):
        try:
            return str(load(open(last_backed_up, "rb")))
        except FileNotFoundError:
            return "Never!"

    def _attempt_backup(self):
        logger.info("called _attempt_backup()")
        self.button.setEnabled(False)
        success = False
        self.button.setText(self.instructions[54])
        self._sleep(1000)
        try:
            success = backup()
        except ServerNotFoundError:
            pass
        if success:
            self.label.setText(self.instructions[52] % self._last_backed_up)
            self.button.setText(self.instructions[55])
        else:
            self.button.setText(self.instructions[56])
        self.button.setEnabled(True)

    @staticmethod
    def _sleep(t):
        loop = QEventLoop()
        QTimer.singleShot(t, loop.quit)
        loop.exec_()
