"""Define the main Qt widget used for running tests.

"""
from sys import exit
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QErrorMessage
from .argparse import get_parser
from .gui import GUIWidget
from .paths import get_test, get_tests_from_batch, get_error_messages


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """Main window.

        Top-level widget for running a test or batch of tests. Called once with no
        arguments when starting the app. Responsible for showing and switching between
        tests and the gui.

        """
        super(MainWindow, self).__init__(parent)

        # get command-line args
        self.args = get_parser().parse_args()

        # print if verbose mode
        self.vprint = print if self.args.verbose else lambda *a, **k: None

        # empty properties to be modified later
        self.args.test_name = None

        # modify test_names if in batch or gui modes
        if self.args.batch_name != "":
            self.args.test_names = get_tests_from_batch(self.batch_name)
        if self.args.gui:
            self.args.test_names = []

        # used for fullscreen mode
        self.desktop_size = QDesktopWidget().availableGeometry().size()

        # start the app
        self.ignore_close_event = False
        self.switch_central_widget()

    def switch_central_widget(self):
        """Show the GUI, move from one test to another, or close the app.

        This method also checks whether a test should be resumed.

        """
        self.vprint("switching the central widget")
        self.args.test_names = [s for s in self.args.test_names if s]
        self.vprint("test list looks like this:", self.args.test_names)

        if len(self.args.test_names) == 0 and self.args.gui:

            self.vprint("no tests; gui mode")
            gui = GUIWidget(self)

            self.vprint('sizing, centring, and showing the window in normal mode')
            if self.isFullScreen():
                self.vprint('in full screen')
                self._sleep(1)
                self.showNormal()  # two calls needed here, unclear why
            self.setFixedSize(gui.sizeHint())
            self._centre()
            self.showNormal()

            self.vprint("showing the gui")
            self.setCentralWidget(gui)

        elif len(self.args.test_names) > 0:

            self.vprint("at least one test")
            self.args.test_name = self.args.test_names.pop(0)

            self.vprint("initalising %s" % self.args.test_name)
            w = get_test(self.args.test_name)
            widget = w(self)

            self.vprint("checking whether there are data already")
            d = widget.data
            data_exist = any([d.test_completed, d.test_resumed, d.test_aborted])
            self.vprint("answer is", data_exist)

            self.vprint("resumable?", self.args.resume)
            if not self.args.resume and data_exist:
                self.vprint("displaying warning message")
                message_box = QErrorMessage(self)
                message = get_error_messages(self.args.language, 'proband_exists')
                message = message % (self.args.proband_id, self.args.test_name)
                message_box.showMessage(message)
                self.switch_central_widget()
                return

            if not self.args.fullscreen:
                self.vprint('sizing, centring, and showing the window in normal mode')
                self.setFixedSize(900, 700)
                widget.setFixedSize(900, 700)
                self._centre()
                self.showNormal()

            else:
                self.vprint('showing the window in fullscreen mode')
                self.setFixedSize(self.desktop_size)
                widget.setFixedSize(self.desktop_size)
                self.showFullScreen()

            self.vprint("showing the test")
            self.setCentralWidget(widget)

            self.vprint("starting the test")
            widget.begin()

        else:

            self.vprint("no tests; no gui; closing")
            exit()

    def _centre(self):
        """Move normal window to centre of screen."""
        rect = self.frameGeometry()
        centre_point = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centre_point)
        self.move(rect.topLeft())

    def _sleep(self, t):
        """PyQt-friendly sleep function."""
        self.ignore_close_event = True
        loop = QEventLoop()
        QTimer.singleShot(t * 1000, loop.quit)
        loop.exec_()
        self.ignore_close_event = False

    def closeEvent(self, event):
        """Reimplemented exit protocol.

        It doesn't make logical sense to exit the entire application when closing a
        test or batch launched from the GUI. This method takes the user back to the GUI
        under such circumstances.

        It also prevents a test from closing when  `ignore_close_event` is True. This is
        used to prevent crashes to desktop when a `closeEvent` events at an awkward time
        during a test, for instance while waiting for a stimulus to disappear from the
        screen.

        If in batch mode, a close event will kill the current test, not the whole batch.

        """
        self.vprint("close event encountered in main window")
        if self.ignore_close_event:
            self.vprint("ignoring close event")
            event.ignore()
        else:
            if isinstance(self.centralWidget(), GUIWidget):
                self.vprint("at the gui, so properly closing")
                exit()
            else:
                self.vprint("at a test, safely closing")
                self.centralWidget().safe_close()
                event.ignore()
