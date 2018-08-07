"""Note-taking widget within gui.

"""
from logging import getLogger

from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)

from .paths import proband_pickles
from .proband import Proband

logger = getLogger(__name__)


class NotesWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Notes widget.

        """
        super(NotesWidget, self).__init__(parent=parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        logger.debug("creating graphical elements of notes widget")

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

        logger.debug("creating a default proband")
        self.proband = None

        # connect
        self.proband_id_box.currentTextChanged.connect(self._load)
        self.save_button.clicked.connect(self._save)
        self.reset_button.clicked.connect(self._reset)

    def _load(self) -> None:
        """Load notes for a given subject."""
        logger.debug("load proband with id: %s" % self.proband_id_box.currentText())
        self.proband = Proband(proband_id=self.proband_id_box.currentText())
        self._reset()

    def _save(self) -> None:
        """Save the notes."""
        self.proband.data["notes"] = self.notes_box.toPlainText()
        self.proband.save()

    def _reset(self) -> None:
        """Reset notes to the saved value."""
        self.notes_box.setPlainText(self.proband.data["notes"])
