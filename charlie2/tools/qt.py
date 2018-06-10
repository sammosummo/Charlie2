from sys import exit
from .argparsing import get_parser
from .data import Data
from .paths import get_test, get_vis_stim_paths, get_aud_stim_paths, get_instructions, get_tests_from_batch
from .gui import GUIWidget
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QSizePolicy, QPushButton, QGridLayout, QDesktopWidget
from PyQt5.QtCore import QTime, QRect, Qt, QTimer, QEventLoop, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent, QFont, QTextDocument


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        """Very top-level instance for running a test or batch of tests. Called
        once when running the application.

        """
        super(MainWindow, self).__init__(parent)

        # get command-line args
        self.args = get_parser().parse_args()
        self.proband_id = self.args.proband_id
        self.test_names = self.args.test_names.split()
        self.language = self.args.language
        self.gui = self.args.gui
        self.fullscreen = self.args.fullscreen

        # empty properties to be modified later
        self.test_name = None
        self.gui_widget = None
        self.test_widget = None

        # modify test_names if in batch or gui modes

        if self.args.batch_name != '':

            self.test_names = get_tests_from_batch(self.args.batch_name)

        if self.gui:

            self.test_names = []

        # start the app
        self.set_central_widget()
        self.show()  # better to be explicit!

    def move_to_centre(self):
        """Move the whole application to centre of the screen. This is used
        when in windowed (not fullscreen) mode.

        """
        rect = self.frameGeometry()
        centre_point = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centre_point)
        self.move(rect.topLeft())

    def set_central_widget(self):
        """This method is used to show the GUI, move from one test to another,
        and close the application if necessary.

        """
        self.test_names = [s for s in self.test_names if s]  # clean up

        if not self.test_names:

            # no tests left; either the end or time to go to GUI

            if self.gui:

                self.showNormal()  # GUI should never be full screen
                self.gui_widget = GUIWidget(self)
                self.setCentralWidget(self.gui_widget)
                self.move_to_centre()

            else:

                exit()  # TODO: figure out Qt-native way to close the app

        else:

            if self.fullscreen:

                self.showFullScreen()  # window size set explicitly elsewhere

            else:

                self.showNormal()

            # pop a test from the list and run it
            self.test_name = self.test_names.pop(0)
            self.test_widget = get_test(self.test_name)
            self.setCentralWidget(self.test_widget(self))
            self.move_to_centre()

    def closeEvent(self, event):
        """It doesn't make logical sense to exit the entire application when
        closing a test or batch launched from the GUI. This method takes the
        user back to the GUI under such circumstances.

        """
        if self.gui and self.centralWidget() != self.gui_widget:

            self.test_names = []
            self.set_central_widget()
            event.ignore()  # without this, Qt will still process close event

        else:

            event.accept()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for test widgets. Not called directly.

        """
        super(ExpWidget, self).__init__(parent)

        # just to save some keystrokes
        p = self.parent().proband_id
        t = self.parent().test_name
        l = self.parent().language

        # create data instance and add some attributes
        self.data = Data(p, t)
        self.data.language = l
        self.data.current_trial_details = None
        self.data.first_trial = True
        self.data.first_block = True

        # paths to stimuli
        self.visual_stimuli = get_vis_stim_paths(t)
        self.auditory_stimuli = get_aud_stim_paths(t)

        # load instructions
        self.instructions = get_instructions(t, l)
        self.instructions_font = QFont('Helvetica', 24)  # big and legible
        # TODO: add font hint here in case Helvetica is not installed

        # set the window size

        if self.parent().fullscreen:

            desktop_size = QDesktopWidget().availableGeometry().size()
            self.setFixedSize(desktop_size)
            self.parent().setFixedSize(desktop_size)

        else:

            size = (700, 700)
            self.setFixedSize(*size)
            self.parent().setFixedSize(*size)

        # create a special label for instructions
        self.instructions_label = QLabel('', self)
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.instructions_label.setFont(self.instructions_font)
        self.instructions_label.resize(self.size())
        self.instructions_label.hide()

        # create a special continue button
        self.continue_button = QPushButton('', self)
        self.continue_button.setText(self.instructions[1])
        self.continue_button.resize(self.continue_button.sizeHint())
        self.continue_button.clicked.connect(self._trial)
        x = round((self.geometry().width() - self.continue_button.width()) / 2)
        y = self.geometry().height() - (self.continue_button.height() + 20)
        self.continue_button.move(x, y)
        self.continue_button.hide()

        # create some more special attributes and widgets
        self.doing_trial = False
        self.countdown = 5
        self.clickable_zones = []
        self.test_time = QTime()
        self.block_time = QTime()
        self.trial_time = QTime()

        # create a painter widget
        self.painter = None

        # used when moving widgets around
        self.x = self.frameGeometry().center().x()
        self.y = self.frameGeometry().center().y()

        # start timers
        self.test_time.start()
        self.block_time.start()  # allows us to use .restart() without issues
        self.trial_time.start()  # allows us to use .restart() without issues

        # begin trials
        self._step()

    def _step(self):
        """Step forward in the test. This could be displaying instructions at
        the start of the test (or a block of trials within the test), starting
        the next trial, or continuing to the next test.

        """

        if self.data.test_done is True:

            self.continue_to_next_test()

        else:

            if self.data.control is None:

                self.data.control = self.gen_control()

            # grab details of current trial from control list
            self.data.current_trial_details = self.data.control.pop(0)

            # figure out if this is the first trial in a new block
            n = self.data.current_trial_details['trial']
            self.data.first_trial = n == 0

            if self.data.first_trial is True:

                self._block()

            else:

                self._trial()

    def _block(self):
        """Runs at the start of a new block of trials. Typically this is used
        to give the proband a break or display new instructions.

        """
        self.block()
        self.continue_button.show()

    def _trial(self):
        """Runs at the start of a new trial. Displays the countdown if first
        in a new block, checks if very last trial, flags the fact that a trial
        is in progress, updates the results list.

        """
        if len(self.data.control) == 0:

            self.data.test_done = True

        if self.data.first_trial:

            self.display_countdown(self.countdown)

        self.doing_trial = True
        self.trial()
        self.data.results.append(self.data.current_trial_details)

    def block(self):
        """Override this method."""
        pass

    def trial(self):
        """Override this method."""
        pass

    def summarise(self):
        """Override this method."""
        pass

    def load_image(self, s, hidden=True):
        """Returns a QLabel containing the image `s`. It is possibly important
        to explicitly set the size of the label after setting its pixmap since
        it does not inherit this attribute automatically, even if the entire
        pixmap is visible.

        """
        label = QLabel(self)
        pixmap = QPixmap(self.visual_stimuli[s])
        label.setPixmap(pixmap)
        label.resize(pixmap.size())

        if hidden:

            label.hide()

        return label

    def make_clickable_zones(self, rects, reset=True):
        """Clickable zones are rects in which mousePressEvents should be
        registered.

        """

        if reset:

            self.clickable_zones = []

        for rect in rects:

            self.clickable_zones.append(rect)

    def continue_to_next_test(self):
        """Move on to the next test. This is a wrapper for a parent method
        because some tests have additional stopping rules and I don't want to
        have to call parent().

        """
        self.data.summary.update(self.summarise())
        self.parent().set_central_widget()

    def display_instructions(self, s, clear=False):
        """Display a set of instructions on the screen."""
        if clear:

            self._remove_all_other_labels()

        self.instructions_label.setText(s)
        self.instructions_label.show()

    def sleep(self, t):
        """PyQt-friendly sleep function."""
        loop = QEventLoop()
        QTimer.singleShot(t * 1000, loop.quit)
        loop.exec_()

    def display_countdown(self, t):
        """Display the countdown timer.

        """
        self.instructions_label.hide()
        self.continue_button.hide()

        for i in range(t):

            self.display_instructions(self.instructions[0] % (t - i))
            self.sleep(.1)

        self.instructions_label.hide()

    def _pos2point(self, pos):
        """Moving a widget to the desired location is kinda annoying in Qt.
        Positions are defined relative to the top left of the window. For our
        purposes its more convenient to define positions relative to the centre
        of the window instead. This method takes a relative-to-centre (x, y)
        tuple of integers and converts it to a point object.

        """
        x, y = pos
        x = self.x + x
        y = self.y - y
        return QPoint(x, y)

    def move_widget(self, widget, pos, show=True):
        """Move a widget to a new position and show it. Returns the new
        widget geometry.

        """
        point = self._pos2point(pos)
        g = widget.frameGeometry()
        g.moveCenter(point)
        widget.move(g.topLeft())

        if show:

            widget.show()

        return g

    def next_trial(self):
        """Just a wrapper around _step()"""
        self._step()

    def _remove_all_other_labels(self):
        """Remove all other labels besides the instructions label.

        """
        for child in self.children():

            if type(child) == QLabel and child != self.instructions_label:

                child.deleteLater()