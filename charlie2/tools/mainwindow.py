"""Define the main Qt widget used for running tests.

"""
from logging import getLogger
from sys import exit
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow
from .data import defaults_for_mainwidow
from .gui import GUIWidget
from .paths import get_test


logger = getLogger(__name__)
window_size = (1000, 750)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """Main window.

        Top-level widget for running a test or batch of tests. Called once with no
        arguments when starting the app. Responsible for showing and switching between
        tests and the gui.

        """
        super(MainWindow, self).__init__(parent)
        logger.info("main window created")

        logger.info("loading default keywords")
        self.kwds = defaults_for_mainwidow
        logger.info("keywords are %s" % str(self.kwds))

        logger.info("getting desktop dimensions")
        self.desktop_size = QDesktopWidget().availableGeometry().size()
        logger.info("dimensions are %s" % str(self.desktop_size))

        logger.info("starting the app proper")
        self.ignore_close_event = False
        self.switch_central_widget()

    def switch_central_widget(self):
        """Switch the central widget.
        
        Show the GUI, move from one test to another, or close the app. This method
        also checks whether a test should be resumed.

        """
        logger.info("called switch_central_widget()")

        logger.info("removing empty test names")
        self.kwds["test_names"] = [s for s in self.kwds["test_names"] if s]
        logger.info("test list looks like this: %s" % str(self.kwds["test_names"]))

        if len(self.kwds["test_names"]) == 0 and self.kwds["gui"] is True:

            logger.info("initialising gui")
            gui = GUIWidget(self)

            logger.info("sizing, centring, and showing the window")
            if self.isFullScreen():
                logger.info("in full screen")
                self.showNormal()  # TODO: Do I need this extra call?
            self.setFixedSize(gui.sizeHint())
            self._centre()
            self.showNormal()  # TODO: Do I need this extra call?

            logger.info("showing the gui")
            self.setCentralWidget(gui)

        elif len(self.kwds["test_names"]) > 0:

            logger.info("at least one test in test_names")
            self.kwds["test_name"] = self.kwds["test_names"].pop(0)

            # logger.info("data for this proband and test?")
            # data_exist = exists(SimpleProcedure(**vars(self.kwds)).path)
            # logger.info("answer is %s" % data_exist)
            #
            # if data_exist:
            #     logger.info("resumable? %s" % self.kwds["resume"])
            #     if not self.kwds["resume"]:
            #         logger.info("displaying warning message")
            #         message_box = QErrorMessage(self)
            #         msg = get_error_messages(self.kwds["language"], "proband_exists")
            #         message = msg % (self.kwds["proband_id"], self.kwds["test_name"])
            #         message_box.setMinimumSize(400, 600)
            #         message_box.showMessage(message)
            #         self.switch_central_widget()
            #         return

            logger.info("initalising %s" % self.kwds["test_name"])
            w = get_test(self.kwds["test_name"])
            widget = w(self)

            if not self.kwds["fullscreen"] or self.kwds["platform"] == "darwin":
                logger.info("showing the window in normal mode")
                self.setFixedSize(*window_size)
                widget.setFixedSize(*window_size)
                self._centre()
                self.showNormal()

            else:
                logger.info("showing the window in fullscreen mode")
                self.setFixedSize(self.desktop_size)
                widget.setFixedSize(self.desktop_size)
                self.showFullScreen()

            logger.info("showing the test")
            self.setCentralWidget(widget)

            logger.info("starting the test")
            widget.begin()

        else:

            logger.info("closing the mainwindow (i.e., everything")
            exit()

    def _centre(self):
        """Move normal window to centre of screen."""
        rect = self.frameGeometry()
        centre_point = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centre_point)
        self.move(rect.topLeft())

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
