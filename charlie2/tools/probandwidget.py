"""Proband widget within gui.

"""
from logging import getLogger
from os import remove
from re import match

from PyQt5.QtWidgets import (
    QComboBox,
    QErrorMessage,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .paths import get_error_messages, proband_pickles
from .proband import Proband

logger = getLogger(__name__)


class ProbandWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Proband tab widget.

        """
        super(ProbandWidget, self).__init__(parent=parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # instructions
        self.instructions = self.parent().instructions

        # layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # layout > proband ID group box
        self.proband_id_groupbox = QGroupBox(self.instructions[6])
        self.layout.addWidget(self.proband_id_groupbox)
        self.proband_id_groupbox_grid = QGridLayout()
        self.proband_id_groupbox.setLayout(self.proband_id_groupbox_grid)
        self.proband_id_groupbox_grid.addWidget(QLabel(self.instructions[7]), 0, 0)

        # layout > proband ID group box > proband ID editable box
        self.proband_id_box = QComboBox()
        self.proband_id_groupbox_grid.addWidget(self.proband_id_box, 0, 1)
        self.proband_id_box.setEditable(True)
        self.proband_id_groupbox_grid.addWidget(
            QLabel(self.instructions[8]), 2, 0, 1, 0
        )

        # layout > additional info group box
        self.addinf_groupbox = QGroupBox(self.instructions[23])
        self.layout.addWidget(self.addinf_groupbox)
        self.addinf_groupbox_grid = QGridLayout()
        self.addinf_groupbox.setLayout(self.addinf_groupbox_grid)
        l = QLabel(self.instructions[24])
        self.addinf_groupbox_grid.addWidget(QLabel(self.instructions[24]), 0, 0, 2, 2)
        self.addinf_groupbox_grid.addWidget(QLabel(self.instructions[25]), 2, 0)

        # layout > additional info group box > age box
        self.addinf_age_box = QComboBox(self)
        self.addinf_age_box.setEditable(False)
        self.addinf_age_box.addItems([str(i) for i in range(1, 101)])
        self.addinf_groupbox_grid.addWidget(self.addinf_age_box, 2, 1)

        # layout > additional info group box > sex box
        self.addinf_groupbox_grid.addWidget(QLabel(self.instructions[26]), 3, 0)
        self.addinf_sex_box = QComboBox(self)
        self.addinf_sex_box.setEditable(False)
        self.addinf_sex_box.addItems(["Male", "Female"])
        self.addinf_groupbox_grid.addWidget(self.addinf_sex_box, 3, 1)

        # layout > additional info group box > other IDs box
        self.addinf_groupbox_grid.addWidget(QLabel(self.instructions[27]), 4, 0)
        self.addinf_otherids_box = QComboBox(self)
        self.addinf_otherids_box.setEditable(True)
        self.addinf_groupbox_grid.addWidget(self.addinf_otherids_box, 5, 0, 1, 2)
        self.addinf_otherids_addbtn = QPushButton(self.instructions[28])
        self.addinf_groupbox_grid.addWidget(self.addinf_otherids_addbtn, 6, 0)
        self.addinf_otherids_rmbtn = QPushButton(self.instructions[29])
        self.addinf_groupbox_grid.addWidget(self.addinf_otherids_rmbtn, 6, 1)

        # layout > save group box
        self.save_groupbox = QGroupBox(self.instructions[50])
        self.layout.addWidget(self.save_groupbox)
        self.save_gird = QGridLayout()
        self.save_groupbox.setLayout(self.save_gird)

        # layout > save group box > save button
        self.save_button = QPushButton(self.instructions[30])
        self.save_gird.addWidget(self.save_button, 0, 0)
        self.delete_button = QPushButton(self.instructions[49])
        self.save_gird.addWidget(self.delete_button, 1, 0)

        # layout > stretch factor
        self.layout.addStretch(1)

        # create a default proband
        self.proband = None

        # connect proband ID box
        self.proband_id_box.currentTextChanged.connect(self._set_proband)

        # connect buttons
        self.addinf_otherids_addbtn.clicked.connect(self._add_other_id)
        self.addinf_otherids_rmbtn.clicked.connect(self._rm_other_id)
        self.save_button.clicked.connect(self._save_proband)
        self.delete_button.clicked.connect(self._delete_proband)
        self._update()

    def _update(self) -> None:
        """Update all fields in this widget."""
        self.proband_id_box.currentTextChanged.disconnect()
        self.proband_id_box.clear()
        self.proband_id_box.addItems([""] + proband_pickles())
        self.addinf_otherids_box.clear()
        if self.proband is not None:
            self.proband_id_box.setCurrentText(self.proband.proband_id)
            self.addinf_age_box.setCurrentText(str(self.proband.age))
            self.addinf_sex_box.setCurrentText(self.proband.sex)
            self.addinf_otherids_box.addItems(sorted(self.proband.other_ids))
        self.proband_id_box.currentTextChanged.connect(self._set_proband)

    def _set_proband(self, s: str) -> None:
        """Creates a new proband object, if valid."""
        if self._valid_proband_id(s):
            self.proband = Proband(proband_id=s)
            self._update()

    def _add_other_id(self) -> None:
        """Add other ID to other-IDs set."""
        b = self.addinf_otherids_box
        other_ids = sorted({b.itemText(i) for i in range(b.count())})
        s = self.addinf_otherids_box.currentText()
        if self._valid_proband_id(s) and s not in other_ids:
            self.addinf_otherids_box.addItem(s)
        else:
            self._invalid_id()

    def _rm_other_id(self) -> None:
        """Add other ID to other IDs set."""
        b = self.addinf_otherids_box
        other_ids = sorted({b.itemText(i) for i in range(b.count())})
        s = self.addinf_otherids_box.currentText()
        if s in other_ids:
            self.addinf_otherids_box.removeItem(self.addinf_otherids_box.findText(s))

    @staticmethod
    def _invalid_id() -> None:
        """Show warning message about ID being invalid."""
        logger.debug("displaying warning message")
        message_box = QErrorMessage()
        msg = get_error_messages("en", "invalid_id")
        message = msg
        message_box.setMinimumSize(400, 200)
        message_box.showMessage(message)

    def _save_proband(self) -> None:
        """Save the current selection."""
        if self._valid_proband_id(self.proband_id_box.currentText()):
            b = self.addinf_otherids_box
            kwds = {
                "proband_id": self.proband_id_box.currentText(),
                "sex": self.addinf_sex_box.currentText(),
                "age": self.addinf_age_box.currentText(),
                "other_ids": sorted({b.itemText(i) for i in range(b.count())}),
            }
            self.proband = Proband(**kwds)
            self.proband.save()
        else:
            self._invalid_id()

    def _delete_proband(self) -> None:
        """Delete the ID."""
        if self.proband.proband_id in proband_pickles():
            remove(self.proband.path)
            self._set_proband(proband_pickles()[0])

    @staticmethod
    def _valid_proband_id(s: str) -> bool:
        """Make sure the proband ID contains is not empty, contains no spaces, and no
        special characters besides underscores.

        """
        if s and match("^[a-zA-Z0-9_]*$", s):
            logger.debug(s + " is a valid proband id")
            return True
        else:
            logger.debug(s + " is a invalid")
            return False
