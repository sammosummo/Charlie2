"""Define the main Qt widget used for running tests.

"""
from logging import getLogger
from sys import exit, platform
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QErrorMessage
from .commandline import get_parser
from .gui import GUIWidget
from .paths import get_test, get_tests_from_batch, get_error_messages


logger = getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """Main window.

        Top-level widget for running a test or batch of tests. Called once with no
        arguments when starting the app. Responsible for showing and switching between
        tests and the gui.

        """
        super(MainWindow, self).__init__(parent)
        logger.info("main window created")

        # format/get command-line arguments
        self.args = get_parser().parse_args()
        self.args.test_name = None  # empty properties to be modified later
        if isinstance(self.args.other_ids, str):
            self.args.other_ids = set(self.args.other_ids.split())
        if self.args.batch_name != "":
            self.args.test_names = get_tests_from_batch(self.batch_name)
        if self.args.gui:
            self.args.test_names = []
        logger.info("command-line arguments are: %s" % str(vars(self.args)))

        # used for full-screen mode
        self.desktop_size = QDesktopWidget().availableGeometry().size()
        logger.info("desktop dimensions: %s" % str(self.desktop_size))

        # start the app proper
        self.ignore_close_event = False
        self.switch_central_widget()

    def switch_central_widget(self):
        """Show the GUI, move from one test to another, or close the app. This method
        also checks whether a test should be resumed.

        """
        logger.info("called switch_central_widget()")
        self.args.test_names = [s for s in self.args.test_names if s]
        logger.info("test list looks like this: %s" % str(self.args.test_names))

        if len(self.args.test_names) == 0 and self.args.gui:

            logger.info("no tests; in gui mode")
            gui = GUIWidget(self)

            logger.info("sizing, centring, and showing the window in normal mode")
            if self.isFullScreen():
                logger.info("in full screen")
                if platform == "darwin":
                    logger.info("running on macOS, so sleeping for 1 second")
                    self._sleep(1)
                self.showNormal()  # two calls needed here, unclear why
            self.setFixedSize(gui.sizeHint())
            self._centre()
            self.showNormal()

            logger.info("showing the gui")
            self.setCentralWidget(gui)

        elif len(self.args.test_names) > 0:

            logger.info("at least one test")
            self.args.test_name = self.args.test_names.pop(0)

            logger.info("initalising %s" % self.args.test_name)
            w = get_test(self.args.test_name)
            widget = w(self)

            logger.info("checking whether there are data already")
            data_exist = any([widget.data.test_completed, widget.data.test_resumed])
            logger.info("answer is %s" % data_exist)

            if data_exist:
                logger.info("resumable? %s" % self.args.resume)
                if not self.args.resume:
                    logger.info("displaying warning message")
                    message_box = QErrorMessage(self)
                    message = get_error_messages(self.args.language, 'proband_exists')
                    message = message % (self.args.proband_id, self.args.test_name)
                    message_box.showMessage(message)
                    self.switch_central_widget()
                    return

            if not self.args.fullscreen:
                logger.info('sizing, centring, and showing the window in normal mode')
                self.setFixedSize(900, 700)
                widget.setFixedSize(900, 700)
                self._centre()
                self.showNormal()

            else:
                logger.info('showing the window in fullscreen mode')
                self.setFixedSize(self.desktop_size)
                widget.setFixedSize(self.desktop_size)
                self.showFullScreen()

            logger.info("showing the test")
            self.setCentralWidget(widget)

            logger.info("starting the test")
            widget.begin()

        else:

            logger.info("no tests; no gui; closing")
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
        logger.info("close event encountered in main window")
        if self.ignore_close_event:
            logger.info("ignoring close event")
            event.ignore()
        else:
            if isinstance(self.centralWidget(), GUIWidget):
                logger.info("at the gui, so properly closing")
                exit()
            else:
                logger.info("at a test, safely closing")
                self.centralWidget().safe_close()
                event.ignore()
