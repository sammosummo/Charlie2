from .argparsing import get_parser
from .data import Data
from .defaults import window_size
from .paths import get_test, get_vis_stim_paths, get_aud_stim_paths, get_common_vis_stim_paths, get_common_aud_stim_paths, get_instructions, get_tests_from_batch
from PyQt5.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):

    def __init__(self):
        """Very top-level instance for running a test or batch of tests."""
        super(MainWindow, self).__init__()
        self.args = get_parser().parse_args()
        self.proband_id = self.args.proband_id
        self.test_names = self.args.test_names.split()
        self.test_name = None

        if self.args.batch_name != '':

            self.test_names = get_tests_from_batch(self.args.batch_name)

        self.language = self.args.language
        self.setFixedSize(*window_size)
        self.setStyleSheet("background-color:lightGray;")
        self.set_central_widget()
        self.show()

    def set_central_widget(self):

        if self.test_names:

            self.test_name = self.exp_names.pop(0)
            widget = get_test(self.test_name)
            self.setCentralWidget(widget(self))

        else:

            self.close()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for test widgets."""
        super(ExpWidget, self).__init__(parent)
        proband_id = self.parent().proband_id
        test_name = self.parent().test_name
        self.data = Data(proband_id, test_name)
        self.vis_stim_dic = get_vis_stim_paths(self.test_name)
        self.aud_stim_dic = get_aud_stim_paths(self.test_name)
        self.vis_stim_path = os.path.join(vis_stim_path, e_)
        self.window_size = (768, 521)
        self.iti = 2
        self.current_trial_details = None
        self.exp_time = QTime()
        self.trial_time = QTime()

        # generate a control sequence if not found in data object

        if not self.data_obj.control and not self.data_obj.exp_done:

            self.data_obj.control = self.gen_control()

        # run experiment-specific setup method

        self.setup()

        # show on screen

        self.setStyleSheet("background-color:lightGray;")
        self.setMinimumSize(*self.window_size)
        self.exp_time.start()
        self.trial_time.start()
        self.show()

    def resize_window(self, resize_main_window=True):
        """Resize the current widget and optionally also the main window.

        """
        self.setFixedSize(*self.window_size)

        if resize_main_window is True:

            self.parent().setFixedSize(*self.window_size)

    def gen_control(self):
        """Override this method.

        """

        pass

    def setup(self):
        """Override this method.

        """

        pass

    def next_trial(self):
        """Override this method.

        """

        pass

    def save(self):

        self.data_obj.save()
