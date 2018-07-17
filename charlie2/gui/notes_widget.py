"""Note-taking widget within gui.

"""
from copy import copy
from logging import getLogger
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QPlainTextEdit,
)
from ..tools.defaults import default_kwds, valid_for_probands
from ..tools.data import Proband
from ..tools.paths import proband_pickles


logger = getLogger(__name__)


class NotesWidget(QWidget):
    def __init__(self, parent=None):
        """Notes widget.

        """
        super(NotesWidget, self).__init__(parent=parent)

        logger.info("creating graphical elements of notes widget")

        # instructions
        self.instructions = self.parent().instructions

        # layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # layout > proband ID selection box
        self.layout.addWidget(QLabel(self.instructions[47]), 0, 0)
        self.proband_id_box = QComboBox()
        self.layout.addWidget(self.proband_id_box, 0, 1)
        self.proband_id_box.setEditable(False)
        self.proband_id_box.addItems(proband_pickles())

        # layout > notes box
        self.notes_box = QPlainTextEdit()
        self.layout.addWidget(self.notes_box, 1, 0, 10, 2)

        # layout > save button
        self.save_button = QPushButton(self.instructions[44])
        self.layout.addWidget(self.save_button, 12, 0)

        # layout > reset button
        self.reset_button = QPushButton(self.instructions[45])
        self.layout.addWidget(self.reset_button, 12, 1)

        # layout > stretch factor
        # self.layout.addStretch(1)

        logger.info("creating a default proband")
        self.dk = {k: v for k, v in default_kwds.items() if k in valid_for_probands}
        self.kwds = copy(self.dk)
        self.proband = Proband(**self.kwds)

        # connect
        self.proband_id_box.currentTextChanged.connect(self._load)
        self.save_button.clicked.connect(self._save)
        self.reset_button.clicked.connect(self._reset)

    def _load(self):
        """Load notes for a given subject."""
        logger.info("load proband with id: %s" % self.proband_id_box.currentText())
        self.proband = Proband(proband_id=self.proband_id_box.currentText())
        self._reset()

    def _save(self):
        """Save the notes."""
        self.proband.data["notes"] = self.notes_box.toPlainText()
        self.proband.save()

    def _reset(self):
        """Reset notes to the saved value."""
        self.notes_box.setPlainText(self.proband.data["notes"])


