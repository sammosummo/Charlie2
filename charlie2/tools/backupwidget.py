"""Defines a Qt widget for backing up data to Google Drive.

"""
from logging import getLogger
from pickle import load

from httplib2 import ServerNotFoundError
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from charlie2.tools.googledrive import backup
from charlie2.tools.paths import last_backed_up

logger = getLogger(__name__)


class BackupWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Backup widget.

        Contains a button which attempts to backup the local data to Google Drive when
        pushed."""
        # TODO: Currently uploading overwrites identical files previously uploaded.
        super(BackupWidget, self).__init__(parent=parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # instructions
        self.instructions = self.parent().instructions

        # layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # layout > last-backed-up message
        self.label = QLabel(self.instructions[52] % self._last_backed_up)
        self.layout.addWidget(self.label)

        # layout > backup button
        self.button = QPushButton(self.instructions[53])
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self._attempt_backup)

        # layout > stretch factor
        self.layout.addStretch(1)

    @property
    def _last_backed_up(self) -> str:
        """Returns timestamp of last backup."""
        try:
            return str(load(open(last_backed_up, "rb")))
        except FileNotFoundError:
            return "Never!"

    def _attempt_backup(self) -> None:
        """Try to back up."""
        logger.debug("called _attempt_backup()")
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
    def _sleep(t) -> None:
        """Used to pause for 1 s before attempting to back up. Allows the message within
        the button to be visible.

        """
        loop = QEventLoop()
        QTimer.singleShot(t, loop.quit)
        loop.exec_()
