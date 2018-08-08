"""Tests widget within the GUI.

"""
from logging import getLogger
from os.path import exists

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from .paths import (
    batches_list,
    get_error_messages,
    get_tests_from_batch,
    proband_pickles,
    tests_list,
)
from .procedure import SimpleProcedure

logger = getLogger(__name__)

keywords = {
    "proband_id",
    "test_name",
    "language",
    "fullscreen",
    "resumable",
}


class TestsWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Test tab widget.

        """
        super(TestsWidget, self).__init__(parent=parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # instructions
        self.instructions = self.parent().instructions

        # layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # layout > options group box
        self.options_groupbox = QGroupBox(self.instructions[9])
        self.layout.addWidget(self.options_groupbox)
        self.options_groupbox_grid = QGridLayout()
        self.options_groupbox.setLayout(self.options_groupbox_grid)

        # layout > options group box > proband ID selection box
        self.options_groupbox_grid.addWidget(QLabel(self.instructions[47]), 0, 0)
        self.proband_id_box = QComboBox()
        self.options_groupbox_grid.addWidget(self.proband_id_box, 0, 1)
        self.proband_id_box.setEditable(False)
        self.options_groupbox_grid.addWidget(QLabel(self.instructions[46]), 1, 0, 3, 2)

        # layout > options group box > fullscreen
        self.fullscreen_checkbox = QCheckBox(self.instructions[10], self)
        self.options_groupbox_grid.addWidget(self.fullscreen_checkbox, 4, 0, 1, 2)

        # layout > options group box > resume
        self.resume_checkbox = QCheckBox(self.instructions[11], self)
        self.options_groupbox_grid.addWidget(self.resume_checkbox, 5, 0, 1, 2)

        # layout > options group box > language selection box
        self.options_groupbox_grid.addWidget(QLabel(self.instructions[48]), 7, 0)
        self.language_box = QComboBox()
        self.options_groupbox_grid.addWidget(self.language_box, 7, 1)
        self.language_box.setEditable(False)

        # layout > test group box
        self.test_groupbox = QGroupBox(self.instructions[13])
        self.layout.addWidget(self.test_groupbox)
        self.test_groupbox_grid = QGridLayout()
        self.test_groupbox.setLayout(self.test_groupbox_grid)

        # layout > test group box > test selection box
        self.test_groupbox_grid.addWidget(QLabel(self.instructions[14]), 0, 0)
        self.test_name_box = QComboBox(self)
        self.test_groupbox_grid.addWidget(self.test_name_box, 0, 1)
        self.test_name_box.setEditable(False)

        # layout > test group box > run test button
        self.test_button = QPushButton(self.instructions[15], self)
        self.test_groupbox_grid.addWidget(self.test_button, 1, 0, 1, 2)

        # layout > batch group box
        self.batch_groupbox = QGroupBox(self.instructions[16])
        self.layout.addWidget(self.batch_groupbox)
        self.batch_groupbox_grid = QGridLayout()
        self.batch_groupbox.setLayout(self.batch_groupbox_grid)

        # layout > batch group box > batch selection box
        self.batch_groupbox_grid.addWidget(QLabel(self.instructions[17]), 0, 0)
        self.batch_name_box = QComboBox(self)
        self.batch_groupbox_grid.addWidget(self.batch_name_box, 0, 1)
        self.batch_name_box.setEditable(False)
        self.batch_groupbox_grid.addWidget(QLabel(self.instructions[21]), 1, 0, 1, 2)

        # layout > batch group box > run batch button
        self.batch_button = QPushButton(self.instructions[18], self)
        self.batch_groupbox_grid.addWidget(self.batch_button, 2, 0, 1, 2)

        # layout > stretch factor
        self.layout.addStretch(1)

        # populate
        logger.debug("creating default keywords")
        keywords = ("proband_id", "test_name", "language", "fullscreen", "resumable")
        kwds = self.parent().parent().kwds.items()
        self.kwds = {k: v for k, v in kwds if k in keywords}
        self.proband_id_box.addItems(["TEST"] + proband_pickles())
        self.fullscreen_checkbox.setChecked(self.kwds["fullscreen"])
        self.resume_checkbox.setChecked(self.kwds["resumable"])
        self.language_box.addItems(["en"])
        self.test_name_box.addItems([""] + sorted(tests_list))
        self.batch_name_box.addItems([""] + sorted(batches_list))

        # connect buttons
        self.__begin = self.parent().parent().switch_central_widget  # store ref
        self.test_button.clicked.connect(self._run_single_test)
        self.batch_button.clicked.connect(self._run_batch)

    def _run_single_test(self) -> None:
        """Run a single test."""
        logger.debug("called _run_single_test()")
        s = self.proband_id_box.currentText()
        if s:
            self.kwds["proband_id"] = s
            self.kwds["fullscreen"] = self.fullscreen_checkbox.isChecked()
            self.kwds["resumable"] = self.resume_checkbox.isChecked()
            self.kwds["language"] = self.language_box.currentText()
            self.kwds["test_names"] = [self.test_name_box.currentText()]
            self._update_maiwindow_kwds()
        rsp = self._show_confirmation_box()
        if rsp == QMessageBox.Ok:
            self._begin()

    def _run_batch(self) -> None:
        """Run a single test."""
        logger.debug("called _run_batch()")
        s = self.proband_id_box.currentText()
        if s:
            self.kwds["proband_id"] = s
            self.kwds["fullscreen"] = self.fullscreen_checkbox.isChecked()
            self.kwds["resumable"] = self.resume_checkbox.isChecked()
            self.kwds["language"] = self.language_box.currentText()
            batch = self.batch_name_box.currentText()
            if batch in batches_list:
                tests = get_tests_from_batch(batch)
                self.kwds["test_names"] = tests
                self._update_maiwindow_kwds()
        rsp = self._show_confirmation_box()
        if rsp == QMessageBox.Ok:
            self._begin()

    def _show_confirmation_box(self) -> int:
        """Display a pop-up message box."""
        logger.debug("called _show_confirmation_box()")
        message_box = QMessageBox()
        s = self.instructions[57] % (
            self.kwds["proband_id"], '\n'.join(self.kwds["test_names"])
        )
        message_box.setText(s)
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return message_box.exec_()

    def _begin(self) -> None:
        logger.debug("called _begin()")
        data = SimpleProcedure(
            proband_id=self.kwds["proband_id"], test_name=self.kwds["test_names"][0]
        )
        proband_exists = exists(data.path)
        if proband_exists and not self.kwds["resumable"]:
            message_box = QMessageBox()
            msg = get_error_messages(self.kwds["language"], "proband_exists")
            message_box.setText(msg)
            message_box.exec_()
        else:
            self.__begin()

    def _update_maiwindow_kwds(self) -> None:
        """The following is quite possibly the worst bit of code I've ever written."""
        logger.debug("called _update_maiwindow_kwds()")
        self.parent().parent().parent().parent().parent().kwds.update(self.kwds)
