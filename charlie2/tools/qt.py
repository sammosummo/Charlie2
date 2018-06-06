from .argparsing import get_parser
from .data import Data
from .defaults import window_size
from .paths import get_test, get_vis_stim_paths, get_aud_stim_paths, get_instructions, get_tests_from_batch
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QTime


class MainWindow(QMainWindow):

    def __init__(self):
        """Very top-level instance for running a test or batch of tests. Called
        once when running the programme.

        """
        super(MainWindow, self).__init__()
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
        self.close()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for test widgets. Not called directly. Contains commonly
        used attributes and methods necessary for running a test, such as
        `next_trial()`, `save()`, and so on.

        """
        super(ExpWidget, self).__init__(parent)
        self.proband_id = self.parent().proband_id
        self.test_name = self.parent().test_name
        self.data = Data(self.proband_id, self.test_name)
        self.visual_stimuli = get_vis_stim_paths(self.test_name)
        self.auditory_stimuli = get_aud_stim_paths(self.test_name)
        self.language = self.parent().language
        self.instructions = get_instructions(self.test_name, self.language)
        self.current_trial_details = None
        self.test_time = QTime()
        self.trial_time = QTime()

        if not self.data_obj.control and not self.data_obj.test_done:

            self.data_obj.control = self.gen_control()

        self.setup()
        # self.setStyleSheet("background-color:lightGray;")
        # self.setMinimumSize(*self.window_size)
        self.test_time.start()
        self.show()

    def resize_window(self, resize_main_window=True):
        """Resize the current widget and optionally also the main window."""
        self.setFixedSize(*self.window_size)

        if resize_main_window is True:

            self.parent().setFixedSize(*self.window_size)

    def gen_control(self):
        """Override this method."""
        pass

    def setup(self):
        """Override this method."""
        pass

    def _trial_preamble(self, next_trial):
        """Used to decorate next_trial() so that the timer always starts."""

        def _preamble(s):

            s.test_time.start()
            next_trial(s)

        return _preamble

    @_trial_preamble
    def next_trial(self):
        """Override this method."""
        pass

    def save(self):
        """Save the data."""
        self.data_obj.save()
