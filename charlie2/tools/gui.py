from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
    QTabWidget,
    QPlainTextEdit,
)
from .data import Proband
from .paths import (
    logo_path,
    get_instructions,
    tests_list,
    get_tests_from_batch,
    batches_list,
    get_docstring_html,
    proband_pickles
)


class GUIWidget(QWidget):
    def __init__(self, parent=None):
        """Widget for the front end graphical user interface (GUI). Allows the
        experimenter to choose the proband ID, which tests to run, etc.

        """
        super(GUIWidget, self).__init__(parent=parent)
        self.args = self.parent().args
        self.vprint = print if self.args.verbose else lambda *a, **k: None
        self.instructions = get_instructions("gui", self.args.language)

        # graphical elements

        # layout
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        # layout > logo
        self.img = QLabel()
        self.vbox.addWidget(self.img)
        self.img.setPixmap(QPixmap(logo_path))
        self.img.setAlignment(Qt.AlignCenter)

        # layout > strap line
        self.txt = QLabel(self.instructions[4])
        self.vbox.addWidget(self.txt)
        self.txt.setAlignment(Qt.AlignCenter)

        # layout > tabs
        self.tabs = QTabWidget()
        self.vbox.addWidget(self.tabs)

        # layout > tabs > proband tab
        self.proband_tab = QWidget()
        self.tabs.addTab(self.proband_tab, self.instructions[6])
        self.proband_tab_vbox = QVBoxLayout()
        self.proband_tab.setLayout(self.proband_tab_vbox)

        # layout > tabs > proband tab > proband box
        self.proband_groupbox = QGroupBox(self.instructions[6])
        self.proband_tab_vbox.addWidget(self.proband_groupbox)
        self.proband_grid = QGridLayout()
        self.proband_groupbox.setLayout(self.proband_grid)
        self.proband_grid.addWidget(QLabel(self.instructions[7]), 0, 0)

        # layout > tab > proband tab > proband box > proband ID
        self.proband_id_box = QComboBox()
        self.proband_grid.addWidget(self.proband_id_box, 0, 1)
        self.proband_id_box.setEditable(True)
        self.proband_grid.addWidget(QLabel(self.instructions[8]), 2, 0, 1, 0)

        # layout > tab > proband tab > additional info box
        self.addinf_groupbox = QGroupBox(self.instructions[23])
        self.proband_tab_vbox.addWidget(self.addinf_groupbox)
        self.addinf_grid = QGridLayout()
        self.addinf_groupbox.setLayout(self.addinf_grid)
        self.addinf_grid.addWidget(QLabel(self.instructions[24]), 0, 0, 1, 2)
        self.addinf_grid.addWidget(QLabel(self.instructions[25]), 1, 0)

        # layout > tab > proband tab > additional info box > age box
        self.addinf_age_box = QComboBox(self)
        self.addinf_age_box.setEditable(False)
        self.addinf_age_box.addItems([str(i) for i in range(1, 101)])
        self.addinf_grid.addWidget(self.addinf_age_box, 1, 1)

        # layout > tab > proband tab > additional info box > sex box
        self.addinf_grid.addWidget(QLabel(self.instructions[26]), 2, 0)
        self.addinf_sex_box = QComboBox(self)
        self.addinf_sex_box.setEditable(False)
        self.addinf_sex_box.addItems(["Male", "Female"])
        self.addinf_grid.addWidget(self.addinf_sex_box, 2, 1)

        # layout > tab > proband tab > additional info box > other IDs box
        self.addinf_grid.addWidget(QLabel(self.instructions[27]), 3, 0)
        self.addinf_otherids_box = QComboBox(self)
        self.addinf_otherids_box.setEditable(True)
        self.addinf_grid.addWidget(self.addinf_otherids_box, 4, 0, 1, 2)
        self.addinf_otherids_addbtn = QPushButton(self.instructions[28])
        self.addinf_grid.addWidget(self.addinf_otherids_addbtn, 5, 0)
        self.addinf_otherids_rmbtn = QPushButton(self.instructions[29])
        self.addinf_grid.addWidget(self.addinf_otherids_rmbtn, 5, 1)

        # layout > tab > proband tab > save box
        self.save_groupbox = QGroupBox(self.instructions[30])
        self.proband_tab_vbox.addWidget(self.save_groupbox)
        self.save_gird = QGridLayout()
        self.save_groupbox.setLayout(self.save_gird)

        # layout > tab > proband tab > save box > save button
        self.save_button = QPushButton(self.instructions[30])
        self.save_gird.addWidget(self.save_button, 0, 0)

        # layout > tab > proband tab > stretch factor
        self.proband_tab_vbox.addStretch(1)

        # layout > tab > test tab
        self.test_tab = QWidget()
        self.tabs.addTab(self.test_tab, self.instructions[5])
        self.test_tab_vbox = QVBoxLayout()
        self.test_tab.setLayout(self.test_tab_vbox)

        # layout > tab > test tab > options box
        self.options_groupbox = QGroupBox(self.instructions[9])
        self.test_tab_vbox.addWidget(self.options_groupbox)
        self.options_grid = QGridLayout()
        self.options_groupbox.setLayout(self.options_grid)

        # layout > tab > test tab > options box > full screen
        self.fullscreen_checkbox = QCheckBox(self.instructions[10], self)
        self.options_grid.addWidget(self.fullscreen_checkbox)

        # layout > tab > test tab > options box > resumable
        self.resume_checkbox = QCheckBox(self.instructions[11], self)
        self.options_grid.addWidget(self.resume_checkbox)

        # layout > tab > test tab > options box > backup
        self.backup_checkbox = QCheckBox(self.instructions[12], self)
        self.options_grid.addWidget(self.backup_checkbox)

        # layout > tab > test tab > test box
        self.test_groupbox = QGroupBox(self.instructions[13])
        self.test_tab_vbox.addWidget(self.test_groupbox)
        self.test_grid = QGridLayout()
        self.test_groupbox.setLayout(self.test_grid)
        self.test_grid.addWidget(QLabel(self.instructions[14]), 0, 0)

        # layout > tab > test tab > test box > select test menu
        self.test_name_box = QComboBox(self)
        self.test_grid.addWidget(self.test_name_box, 0, 1)

        # layout > tab > test tab > test box > run test button
        self.test_button = QPushButton(self.instructions[15], self)
        self.test_grid.addWidget(self.test_button, 1, 0, 1, 0)

        # layout > tab > test tab > batch box
        self.batch_groupbox = QGroupBox(self.instructions[16])
        self.test_tab_vbox.addWidget(self.batch_groupbox)
        self.batch_grid = QGridLayout()
        self.batch_groupbox.setLayout(self.batch_grid)
        self.batch_grid.addWidget(QLabel(self.instructions[17]), 0, 0)

        # layout > tab > test tab > test box > select batch file menu
        self.batch_name_box = QComboBox()
        self.batch_grid.addWidget(self.batch_name_box, 0, 1)
        self.batch_button = QPushButton(self.instructions[18], self)
        self.batch_grid.addWidget(self.batch_button, 3, 0, 1, 0)
        self.batch_grid.addWidget(QLabel(self.instructions[21]), 2, 0, 1, 0)

        # layout > tab > test tab > stretch factor
        self.test_tab_vbox.addStretch(1)

        # layout > tab > backup tab
        self.backup_tab = QWidget()
        self.tabs.addTab(self.backup_tab, self.instructions[22])
        self.backup_tab_vbox = QVBoxLayout()
        self.backup_tab.setLayout(self.backup_tab_vbox)

        # layout > tab > backup tab > local data box
        self.local_groupbox = QGroupBox(self.instructions[31])
        self.backup_tab_vbox.addWidget(self.local_groupbox)
        self.local_grid = QGridLayout()
        self.local_groupbox.setLayout(self.local_grid)

        # layout > tab > backup tab > local data box > local data
        self.local_data = QPlainTextEdit()
        self.local_grid.addWidget(self.local_data, 0, 0)
        self.local_data.setPlainText(self.instructions[36])
        self.local_data.setReadOnly(True)
        self.local_data.setFont(QFont('Courier'))
        self.local_data.setMaximumHeight(55)

        # layout > tab > backup tab > remote data box
        self.remote_groupbox = QGroupBox(self.instructions[32])
        self.backup_tab_vbox.addWidget(self.remote_groupbox)
        self.remote_grid = QGridLayout()
        self.remote_groupbox.setLayout(self.remote_grid)

        # layout > tab > backup tab > remote data box > remote data
        self.remote_data = QPlainTextEdit()
        self.remote_grid.addWidget(self.remote_data, 0, 0)
        self.remote_data.setPlainText(self.instructions[36])
        self.remote_data.setReadOnly(True)
        self.remote_data.setFont(QFont('Courier'))
        self.remote_data.setMaximumHeight(55)
        

        # layout > tab > backup tab > status box
        self.status_groupbox = QGroupBox(self.instructions[33])
        self.backup_tab_vbox.addWidget(self.status_groupbox)
        self.status_grid = QGridLayout()
        self.status_groupbox.setLayout(self.status_grid)

        # layout > tab > backup tab > status data box > status data
        self.status_data = QPlainTextEdit()
        self.status_grid.addWidget(self.status_data, 0, 0)
        self.status_data.setReadOnly(True)
        self.status_data.setFont(QFont('Courier'))
        self.status_data.setMaximumHeight(25)

        # layout > tab > backup tab > backup box
        self.backup_groupbox = QGroupBox(self.instructions[34])
        self.backup_tab_vbox.addWidget(self.backup_groupbox)
        self.backup_grid = QGridLayout()
        self.backup_groupbox.setLayout(self.backup_grid)

        # layout > tab > backup tab > backup box > backup button
        self.backup_button = QPushButton(self.instructions[35], self)
        self.backup_grid.addWidget(self.backup_button)

        # layout > tab > test tab > stretch factor
        self.backup_tab_vbox.addStretch(1)










    #     self.fullscreen_checkbox.setChecked(self.args.fullscreen)
    #     self.fullscreen_checkbox.stateChanged.connect(self._toggle_fullscreen)

    # self.resume_checkbox.setChecked(self.args.resume)
    #
    #
    #     self.resume_checkbox.stateChanged.connect(self._toggle_resume)
    #
    #
    #     font = self.backup_checkbox.font()
    #     font.setStrikeOut(True)
    #     self.backup_checkbox.setFont(font)
    #     self.backup_checkbox.setCheckable(False)
    #
    #
    #
    #
    #
    #
    #     self.test_name_box.addItems([""] + tests_list)
    #     self.test_name_box.activated.connect(self._set_test_names_single)
    #
    #
    #     self.test_button.clicked.connect(self.parent().switch_central_widget)
    #
    #
    #
    #
    #
    #
    #
    #     self)
    #     self.batch_name_box.addItems([""] + batches_list)
    #     self.batch_name_box.activated.connect(self._set_test_names_batch)
    #
    #
    #     self.batch_button.clicked.connect(self.parent().switch_central_widget)
    #
    #
    #
    #
    #
    #     self.docs_tab = QWidget()
    #
    #     self.docs_grid = QGridLayout()
    #     self.docs_grid.addWidget(QLabel(self.instructions[20]), 0, 0)
    #     self.docs_name_box = QComboBox(self)
    #     self.docs_name_box.addItems([""] + tests_list)
    #     self.docs_name_box.activated.connect(self._set_test_names_single)
    #     self.docs_grid.addWidget(self.docs_name_box, 0, 1)
    #     self.docs_text_box = QTextBrowser()
    #     self.docs_grid.addWidget(self.docs_text_box, 1, 0, 1, 0)
    #     self.test_button2 = QPushButton(self.instructions[15], self)
    #     self.test_button2.clicked.connect(self.parent().switch_central_widget)
    #     self.docs_grid.addWidget(self.test_button2, 3, 0, 2, 0)
    #     self.docs_tab.setLayout(self.docs_grid)
    #     self.tabs.addTab(self.docs_tab, self.instructions[19])
    #
    #     self.backup_tab = QWidget()
    #
    #     self.backup_grid = QGridLayout()
    #     self.backup_grid.addWidget(QLabel(self.instructions[20]), 0, 0)
    #     self.backup_name_box = QComboBox(self)
    #     self.backup_name_box.addItems([""] + tests_list)
    #     self.backup_name_box.activated.connect(self._set_test_names_single)
    #     self.backup_grid.addWidget(self.backup_name_box, 0, 1)
    #     self.backup_text_box = QTextBrowser()
    #     self.backup_grid.addWidget(self.backup_text_box, 1, 0, 1, 0)
    #     self.test_button2 = QPushButton(self.instructions[15], self)
    #     self.test_button2.clicked.connect(self.parent().switch_central_widget)
    #     self.backup_grid.addWidget(self.test_button2, 3, 0, 2, 0)
    #     self.backup_tab.setLayout(self.backup_grid)
    #     self.tabs.addTab(self.backup_tab, self.instructions[22])
    #
    #     self.vbox.addWidget(self.tabs)
    #
    #
    # def _set_proband_id(self):
    #     """Change the proband ID."""
    #     self.vprint("Proband ID changed to", self.proband_id_box.currentText())
    #     self.args.proband_id = self.proband_id_box.currentText()
    #     self.proband = Proband(**vars(self.args))
    #
    #     if self.args.proband_id in proband_pickles():
    #         self.addinf_age_box.setCurrentText(self.proband.proband_age)
    #         self.addinf_sex_box.setCurrentText(self.proband.proband_sex)
    #         self.addinf_otherids_box.clear()
    #         self.addinf_otherids_box.addItems(self.args.other_ids)
    #         print(self.args)
    #     else:
    #         self.addinf_age_box.setCurrentIndex(0)
    #         self.addinf_sex_box.setCurrentIndex(0)
    #         self.addinf_otherids_box.clear()
    #
    # def _set_proband_age(self):
    #     """Change the proband age."""
    #     self.vprint("Proband age changed to", self.addinf_age_box.currentText())
    #     self.args.proband_age = self.addinf_age_box.currentText()
    #
    # def _set_proband_sex(self):
    #     """Change the proband sex."""
    #     self.vprint("Proband sex changed to", self.addinf_sex_box.currentText())
    #     self.args.proband_sex = self.addinf_sex_box.currentText()
    #
    # def _add_other_id(self):
    #     """Change the proband sex."""
    #     s = self.addinf_otherids_box.currentText()
    #     if s:
    #         self.vprint("Added the ID", s)
    #         self.args.other_ids.add(s)
    #         self.addinf_otherids_box.clear()
    #         self.addinf_otherids_box.addItems(self.args.other_ids)
    #
    # def _remove_other_id(self):
    #     """Change the proband sex."""
    #     s = self.addinf_otherids_box.currentText()
    #     if s in self.args.other_ids:
    #         self.vprint("Removed the ID", s)
    #         self.args.other_ids.remove(s)
    #         self.addinf_otherids_box.clear()
    #         self.addinf_otherids_box.addItems(self.args.other_ids)
    #
    # def _set_test_names_single(self):
    #     """Set the next test to be the selected one."""
    #     self.args.test_names = [self.sender().currentText()]
    #     s = get_docstring_html(self.args.test_names[0])
    #     self.docs_text_box.setText(s)
    #
    # def _set_test_names_batch(self):
    #     """Load the test names from the selected batch file."""
    #     batch_file = self.sender().currentText()
    #     if batch_file:
    #         self.args.test_names = get_tests_from_batch(batch_file)
    #     else:
    #         self.args.test_names = []
    #
    # def _toggle_fullscreen(self, state):
    #     """Toggle fullscreen mode."""
    #     if state == Qt.Checked:
    #         self.args.fullscreen = True
    #     else:
    #         self.args.fullscreen = False
    #
    # def _toggle_resume(self, state):
    #     """Toggle resume mode."""
    #     if state == Qt.Checked:
    #         self.args.resume = True
    #     else:
    #         self.args.resume = False
    #
    # def _save(self):
    #     """Save proband information."""
    #     print(self.args.other_ids)
    #     self.proband = Proband(**vars(self.args), override=True)
    #     self.proband.save()

