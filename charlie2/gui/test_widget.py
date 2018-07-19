"""Test widget within gui.

"""
from copy import copy
from logging import getLogger
from os.path import exists
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QCheckBox,
    QMessageBox,
)
from ..tools.data import SimpleProcedure
from ..tools.defaults import default_kwds, valid_for_tests
from ..tools.paths import (
    tests_list,
    proband_pickles,
    batches_list,
    get_tests_from_batch,
    get_error_messages,
)


logger = getLogger(__name__)


class TestWidget(QWidget):
    def __init__(self, parent=None):
        """Test tab widget.

        """
        super(TestWidget, self).__init__(parent=parent)

        logger.info("creating graphical elements of test widget")

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

        # layout > options group box > autobackup
        self.autobackup_checkbox = QCheckBox(self.instructions[12], self)
        self.options_groupbox_grid.addWidget(self.autobackup_checkbox, 6, 0, 1, 2)

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
        logger.info("creating default keywords")
        self.dk = {k: v for k, v in default_kwds.items() if k in valid_for_tests}
        self.kwds = copy(self.dk)
        self.proband_id_box.addItems(["TEST"] + proband_pickles())
        self.fullscreen_checkbox.setChecked(self.kwds["fullscreen"])
        self.resume_checkbox.setChecked(self.kwds["resume"])
        self.autobackup_checkbox.setChecked(self.kwds["autobackup"])
        self.language_box.addItems(["en"])
        self.test_name_box.addItems([""] + sorted(tests_list))
        self.batch_name_box.addItems([""] + sorted(batches_list))

        # connect buttons
        self.__begin = self.parent().parent().switch_central_widget  # store ref
        self.test_button.clicked.connect(self._run_single_test)
        self.batch_button.clicked.connect(self._run_batch)

    def _run_single_test(self):
        """Run a single test."""
        logger.info("_run_single_test() called")
        s = self.proband_id_box.currentText()
        if s == "TEST":
            logger.info("showing a warning popup because proband is TEST")
            message_box = QMessageBox()
            msg = get_error_messages(self.kwds["language"], "proband_is_TEST")
            message_box.setText(msg)
            message_box.buttonClicked.connect(self.__run_single_test)
            message_box.exec_()
        else:
            self.__run_single_test()

    def __run_single_test(self):
        s = self.proband_id_box.currentText()
        if s:
            self.kwds["proband_id"] = s
            self.kwds["fullscreen"] = self.fullscreen_checkbox.isChecked()
            self.kwds["resume"] = self.resume_checkbox.isChecked()
            self.kwds["autobackup"] = self.autobackup_checkbox.isChecked()
            self.kwds["language"] = self.language_box.currentText()
            self.kwds["test_names"] = [self.test_name_box.currentText()]
            self._update_maiwindow_kwds()
            logger.info("about to run with these kewyords: %s" % str(self.kwds))
            self._begin()

    def _run_batch(self):
        """Run a single test."""
        logger.info("_run_batch() called")
        s = self.proband_id_box.currentText()
        if s == "TEST":
            logger.info("showing a warning popup because proband is TEST")
            message_box = QMessageBox()
            msg = get_error_messages(self.kwds["language"], "proband_is_TEST")
            message_box.setText(msg)
            message_box.buttonClicked.connect(self.__run_batch)
            message_box.exec_()
        else:
            self.__run_batch()

    def __run_batch(self):
        """Run a batch of tests."""
        s = self.proband_id_box.currentText()
        if s:
            self.kwds["proband_id"] = s
            self.kwds["fullscreen"] = self.fullscreen_checkbox.isChecked()
            self.kwds["resume"] = self.resume_checkbox.isChecked()
            self.kwds["autobackup"] = self.autobackup_checkbox.isChecked()
            self.kwds["language"] = self.language_box.currentText()
            batch = self.batch_name_box.currentText()
            if batch in batches_list:
                tests = get_tests_from_batch(batch)
                self.kwds["test_names"] = tests
                self._update_maiwindow_kwds()
                logger.info("about to run with these kewyords: %s" % str(self.kwds))
                self._begin()

    def _begin(self):
        data = SimpleProcedure(
            proband_id=self.kwds["proband_id"],
            test_name=self.kwds["test_names"][0]
        )
        proband_exists = exists(data.path)
        if proband_exists and not self.kwds["resume"]:
            message_box = QMessageBox()
            msg = get_error_messages(self.kwds["language"], "proband_exists")
            message_box.setText(msg)
            message_box.exec_()
        else:
            self.__begin()

    def _update_maiwindow_kwds(self):
        """The following is quite possibly the worst bit of code I've ever written."""
        self.parent().parent().parent().parent().parent().kwds.update(self.kwds)
