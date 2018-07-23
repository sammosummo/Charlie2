"""Create the gui.

"""
from logging import getLogger
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QTabWidget
from .paths import logo_path, get_instructions, proband_pickles
from charlie2.tools.probandwidget import ProbandWidget
from charlie2.tools.testswidget import TestsWidget
from charlie2.tools.noteswidget import NotesWidget
from charlie2.tools.backupwidget import BackupWidget


logger = getLogger(__name__)


class GUIWidget(QWidget):
    def __init__(self, parent=None):
        """Widget for the front end graphical user interface (GUI). Allows the
        experimenter to choose the proband ID, which tests to run, etc.

        """
        super(GUIWidget, self).__init__(parent=parent)
        logger.info(f"initialised {type(self)}")

        self.instructions = get_instructions("gui", self.parent().kwds["language"])

        logger.info("setting proband to None")
        self.proband = None

        logger.info("creating all graphical elements of gui")

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

        # layout > tabs widget
        self.tabs = QTabWidget()
        self.vbox.addWidget(self.tabs)

        # layout > tabs widget > proband tab
        self.proband_tab = QTabWidget()
        self.proband_tab_vbox = QVBoxLayout()
        self.proband_tab.setLayout(self.proband_tab_vbox)
        self.proband_widget = ProbandWidget(self)
        self.proband_tab_vbox.addWidget(self.proband_widget)
        _w = self.proband_widget.sizeHint().width() + 20
        _h = self.proband_widget.sizeHint().height()
        self.proband_tab.setMinimumSize(_w, _h)
        self.tabs.addTab(self.proband_tab, self.instructions[6])

        # layout > tabs widget > test tab
        self.test_tab = QTabWidget()
        self.test_tab_vbox = QVBoxLayout()
        self.test_tab.setLayout(self.test_tab_vbox)
        self.test_widget = TestsWidget(self)
        self.test_tab_vbox.addWidget(self.test_widget)
        _w = self.test_widget.sizeHint().width() + 20
        _h = self.test_widget.sizeHint().height()
        self.test_tab.setMinimumSize(_w, _h)
        self.tabs.addTab(self.test_tab, self.instructions[5])

        # layout > tabs widget > notes tab
        self.notes_tab = QTabWidget()
        self.notes_tab_vbox = QVBoxLayout()
        self.notes_tab.setLayout(self.notes_tab_vbox)
        self.notes_widget = NotesWidget(self)
        self.notes_tab_vbox.addWidget(self.notes_widget)
        _w = self.notes_widget.sizeHint().width() + 20
        _h = self.notes_widget.sizeHint().height()
        self.notes_tab.setMinimumSize(_w, _h)
        self.tabs.addTab(self.notes_tab, self.instructions[42])

        # layout > tabs widget > backup tab
        self.backup_tab = QTabWidget()
        self.backup_tab_vbox = QVBoxLayout()
        self.backup_tab.setLayout(self.backup_tab_vbox)
        self.backup_widget = BackupWidget(self)
        self.backup_tab_vbox.addWidget(self.backup_widget)
        _w = self.backup_widget.sizeHint().width() + 20
        _h = self.backup_widget.sizeHint().height()
        self.backup_tab.setMinimumSize(_w, _h)
        self.tabs.addTab(self.backup_tab, self.instructions[51])

        # connect tab changing to method
        self.tabs.currentChanged.connect(self._update_proband_lists)

    def _update_proband_lists(self):
        """The Tests and Notes tabs have proband boxes that need to be updated."""
        self.test_widget.proband_id_box.clear()
        self.test_widget.proband_id_box.addItems(["TEST"] + sorted(proband_pickles()))
        self.notes_widget.proband_id_box.clear()
        self.notes_widget.proband_id_box.addItems(sorted(proband_pickles()))
