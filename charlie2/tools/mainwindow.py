"""Main Qt widget used for running tests.

"""
from datetime import datetime
from logging import getLogger
from sys import exit, platform

from PyQt5.QtGui import QCloseEvent
from httplib2 import ServerNotFoundError
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from .gui import GUIWidget
from .paths import durations_path, get_test

logger = getLogger(__name__)
window_size = (1000, 750)


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        """Main window.

        Top-level widget for running a test or batch of tests. Called once with no
        arguments when starting the app. Responsible for showing and switching between
        tests and the gui, recording additional proband information, and backing up the
        data.

        """
        super(MainWindow, self).__init__(parent)
        logger.debug(f"initialised {type(self)}")

        logger.debug("loading default keywords")
        self.kwds = {
            "batch_name": None,
            "test_name": None,
            "test_names": [],
            "language": "en",
            "fullscreen": [True, False][platform == "darwin"],
            "resumable": False,
            "gui": True,
        }
        logger.debug("keywords are %s" % str(self.kwds))

        logger.debug("getting desktop dimensions")
        self.desktop_size = QDesktopWidget().availableGeometry().size()
        logger.debug("dimensions are %s" % str(self.desktop_size))

        logger.debug("starting a rough timer")
        self.time_started = datetime.now()

        logger.debug("starting the app proper")
        self.ignore_close_event = False
        self.switch_central_widget()

    def switch_central_widget(self) -> None:
        """Switch the central widget.
        
        Show the GUI, move from one test to another, or close the app. This method
        also checks whether a test should be resumed.

        """
        logger.debug("called switch_central_widget()")

        logger.debug("removing empty test names")
        self.kwds["test_names"] = [s for s in self.kwds["test_names"] if s]

        if len(self.kwds["test_names"]) == 0 and self.kwds["gui"] is True:

            gui = GUIWidget(self)

            logger.debug("sizing, centring, and showing the window")
            if self.isFullScreen():
                logger.debug("in full screen")
                self.showNormal()  # TODO: Do I need this extra call?
            self.setFixedSize(gui.sizeHint())
            self._centre()
            self.showNormal()  # TODO: Do I need this extra call?

            logger.debug("showing the gui")
            self.setCentralWidget(gui)

        elif len(self.kwds["test_names"]) > 0:

            logger.debug("at least one test in test_names")
            self.kwds["test_name"] = self.kwds["test_names"].pop(0)

            logger.debug(f"initialising {self.kwds['test_name']}")
            w = get_test(self.kwds["test_name"])
            widget = w(self)

            if not self.kwds["fullscreen"] or self.kwds["platform"] == "darwin":
                logger.debug("showing the window in normal mode")
                self.setFixedSize(*window_size)
                widget.setFixedSize(*window_size)
                self._centre()
                self.showNormal()

            else:
                logger.debug("showing the window in fullscreen mode")
                self.setFixedSize(self.desktop_size)
                widget.setFixedSize(self.desktop_size)
                self.showFullScreen()

            logger.debug("showing the test")
            self.setCentralWidget(widget)

            logger.debug("starting the test")
            widget.begin()

        else:
            exit()

    def _centre(self) -> None:
        """Move normal window to centre of screen."""
        rect = self.frameGeometry()
        centre_point = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centre_point)
        self.move(rect.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        """Reimplemented exit protocol.

        It doesn't make logical sense to exit the entire application when closing a
        test or batch launched from the GUI. This method takes the user back to the GUI
        under such circumstances.

        It also prevents a test from closing when  `ignore_close_event` is True. This is
        used to prevent crashes to desktop when a `closeEvent` events at an awkward time
        during a test, for instance while waiting for a stimulus to disappear from the
        screen.

        If in batch mode, a close event will kill the current test, not the whole batch.

        Args:
            event:

        """
        logger.debug("close event encountered in main window")
        if self.ignore_close_event:
            logger.debug("ignoring close event")
            event.ignore()
        else:
            if isinstance(self.centralWidget(), GUIWidget):
                logger.debug("at the gui, so properly closing")
                duration = datetime.now() - self.time_started
                s = ",".join([str(duration), str(self.time_started)]) + "\n"
                open(durations_path, "a").write(s)
                exit()
            else:
                logger.debug("at a test, safely closing")
                self.centralWidget().safe_close()
                event.ignore()
