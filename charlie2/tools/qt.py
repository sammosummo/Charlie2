import sys
from .argparsing import get_parser
from .data import Data
from .defaults import window_size
from .paths import get_test, get_vis_stim_paths, get_aud_stim_paths, get_instructions, get_tests_from_batch
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QSizePolicy, QPushButton, QGridLayout
from PyQt5.QtCore import QTime, QRect, Qt
from PyQt5.QtGui import QPixmap, QMouseEvent, QFont


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        """Very top-level instance for running a test or batch of tests. Called
        once when running the programme.

        """
        super(MainWindow, self).__init__(parent)
        self.args = get_parser().parse_args()
        self.proband_id = self.args.proband_id
        self.test_names = self.args.test_names.split()
        self.test_name = None

        if self.args.batch_name != '':

            self.test_names = get_tests_from_batch(self.args.batch_name)

        self.language = self.args.language
        self.setFixedSize(*window_size)
        # self.setStyleSheet("background-color:lightGray;")
        self.startup()
        self.show()

    def startup(self):
        """Start the programme."""
        # TODO: Add startup stuff here.
        self.set_central_widget()

    def set_central_widget(self):
        """Pop the first test on the list an run it; shut down in none left."""

        if self.test_names:

            self.test_name = self.test_names.pop(0)
            widget = get_test(self.test_name)
            self.setCentralWidget(widget(self))

        else:

            self.shutdown()

    def shutdown(self):
        """Close the programme."""
        # TODO: Add shutdown stuff here.
        sys.exit()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for test widgets. Not called directly. Contains commonly
        used attributes and methods necessary for running a test, such as
        `trial()`, `save()`, and so on.

        """
        super(ExpWidget, self).__init__(parent)
        p = self.parent().proband_id
        t = self.parent().test_name
        l = self.parent().language
        self.data = Data(p, t)
        self.visual_stimuli = get_vis_stim_paths(t)
        self.auditory_stimuli = get_aud_stim_paths(t)
        self.clickable_zones = []
        self.data.language = l
        self.instructions = get_instructions(t, l)
        self.instructions_font = QFont('Helvetica', 48)
        self.data.current_trial_details = None
        self.data.first_trial = True
        self.summary = {}
        self.test_time = QTime()
        self.trial_time = QTime()
        self._setup()
        # self.setStyleSheet("background-color:lightGray;")
        # self.setMinimumSize(*self.window_size)

    def resize_window(self, resize_main_window=True):
        """Resize the current widget and optionally also the main window."""
        self.setFixedSize(*self.window_size)

        if resize_main_window is True:

            self.parent().setFixedSize(*self.window_size)

    def gen_control(self):
        """Override this method."""
        pass

    def _setup(self):
        """Preamble to call before test-specific setup."""

        if not self.data.control and not self.data.test_done:

            self.data.control = self.gen_control()

        self.setup()
        self.resize_window(True)
        self.test_time.start()
        self.trial_time.start()
        self._trial()

    def setup(self):
        """Override this method."""
        pass

    def _trial(self):
        """"Preamble to call before test-specific trial."""

        if self.data.test_done:

            print('test is done')
            self.continue_to_next_test()

        self.data.current_trial_details = self.data.control.pop(0)
        self.trial_time.restart()
        self.trial()
        self.data.results.append(self.data.current_trial_details)
        self.data.save()

        if self.data.first_trial:

            self.data.first_trial = False

        if not self.data.control:

            self.data.test_done = True

    def trial(self):
        """Override this method."""
        pass

    def summarise(self):
        """Override this method."""
        pass

    def next_trial(self):
        self._trial()

    def load_image(self, s):
        """Returns a QLabel containing the image `s`."""
        label = QLabel(self)
        label.setPixmap(QPixmap(self.visual_stimuli[s]))
        return label

    def make_clickable_zones(self, zones, reset=False):
        """Reset and make new list of clickable zones."""
        if reset:

            self.clickable_zones = []

        for zone in zones:

            if type(zone) == QRect:

                self.clickable_zones.append(zone)

    def continue_to_next_test(self):
        """Move on to the next test."""
        self.data.summary = self.summarise()
        self.parent().set_central_widget()

    def _display_instructions(self, s):
        """Return a label with text."""
        label = QLabel(s, self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(self.instructions_font)
        # label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return label

    def _display_continue_button(self):
        """Return a continue button."""
        button = QPushButton('Continue', self)
        button.resize(button.sizeHint())
        return button

    def display_instructions(self, s):
        """Display a set of instructions on the screen."""
        layout = QGridLayout()
        label = self._display_instructions(s)
        layout.addWidget(label, 0, 0)
        button = self._display_continue_button()
        layout.addWidget(button, 1, 0)
        self.setLayout(layout)
        self.show()


        # label = QLabel(s, self)
        # label.resize(*self.window_size)
        #

        # label.setFont(self.instructions_font)
        # label.show()




