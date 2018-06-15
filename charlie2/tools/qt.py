from sys import exit
from .argparsing import get_parser
from .data import Data
from .paths import (
    get_test,
    get_vis_stim_paths,
    get_aud_stim_paths,
    get_instructions,
    get_tests_from_batch,
)
from .gui import GUIWidget
from PyQt5.QtCore import QTime, Qt, QTimer, QEventLoop, QPoint
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QDesktopWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """Very top-level instance for running a test or batch of tests. Called once
        when running the application.

        """
        super(MainWindow, self).__init__(parent)

        # get command-line args
        self.args = get_parser().parse_args()
        self.proband_id = self.args.proband_id
        self.test_names = self.args.test_names.split()
        self.language = self.args.language
        self.gui = self.args.gui
        self.fullscreen = self.args.fullscreen
        self.verbose = self.args.verbose

        # empty properties to be modified later
        self.test_name = None
        self.gui_widget = None
        self.test_widget = None

        # modify test_names if in batch or gui modes
        if self.args.batch_name != "":
            self.test_names = get_tests_from_batch(self.args.batch_name)
        if self.gui:
            self.test_names = []

        # start the app
        self.set_central_widget()
        self.show()  # maybe not necessary but better to be explicit!

    def move_to_centre(self):
        """Move the whole application to centre of the screen. This is used when in
        windowed (not fullscreen) mode.

        """
        rect = self.frameGeometry()
        centre_point = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centre_point)
        self.move(rect.topLeft())

    def set_central_widget(self):
        """This method is used to show the GUI, move from one test to another, and close
        the application if necessary.

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
                self.showFullScreen()
            else:
                self.showNormal()
            # pop a test from the list and run it
            self.test_name = self.test_names.pop(0)
            self.test_widget = get_test(self.test_name)
            self.setCentralWidget(self.test_widget(self))
            self.move_to_centre()

    def closeEvent(self, event):
        """It doesn't make logical sense to exit the entire application when closing a
        test or batch launched from the GUI. This method takes the user back to the GUI
        under such circumstances.

        """
        if self.gui and self.centralWidget() != self.gui_widget:
            self.test_names = []
            self.set_central_widget()
            event.ignore()  # without this, Qt will still process close event
        else:
            event.accept()


class ExpWidget(QWidget):
    def __init__(self, parent=None):
        """Base class for test widgets. Not called directly."""
        super(ExpWidget, self).__init__(parent)
        self.vprint = print if self.parent().verbose else lambda *a, **k: None

        # required to accept keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

        # shortcuts variable names to save some keystrokes
        p = self.parent().proband_id
        t = self.parent().test_name
        l = self.parent().language

        # create data instance and add some attributes
        self.data = Data(p, t)
        self.data.language = l
        self.data.current_trial_details = None
        self.data.first_trial = True
        self.data.first_block = True

        # paths to visual stimuli
        self.vis_stim_paths = get_vis_stim_paths(t)

        # load instructions
        self.instructions = get_instructions(t, l)
        self.instructions_font = QFont("Helvetica", 24)  # big and legible

        # set the window size
        if self.parent().fullscreen:
            desktop_size = QDesktopWidget().availableGeometry().size()
            self.setFixedSize(desktop_size)
            self.parent().setFixedSize(desktop_size)
        else:
            size = (700, 700)
            self.setFixedSize(*size)
            self.parent().setFixedSize(*size)

        # configure the block timeout
        self.block_max_time = None

        # create timers
        self.test_time = QTime()
        self.block_time = QTime()
        self.block_timeout_timer = QTimer()
        self.trial_time = QTime()

        # start timers
        self.test_time.start()
        self.block_time.start()
        self.trial_time.start()

        # create zones for clicking
        self.zones = []

        # begin trials
        self._step()

        # configure whether blocks are "silent" (i.e., does not pause before continuing)
        self.block_silent = False

        # configure whether to skip countdowns
        self.skip_countdowns = False

        # enforce showing the mouse
        self.show_mouse()

    def sleep(self, t):
        """PyQt-friendly sleep function."""
        loop = QEventLoop()
        QTimer.singleShot(t * 1000, loop.quit)
        loop.exec_()

    def delete_labels_and_buttons(self, delete=False):
        """Hide and delete all label child widgets. I don't think any other kind of
        widget needs to be deleted/hidden.

        """
        for obj in self.children():
            if isinstance(obj, QLabel) or isinstance(obj, QPushButton):
                obj.hide()
                if delete:
                    obj.deleteLater()

    def display_instructions(self, message):
        """Display a set of instructions on the screen."""
        self.delete_labels_and_buttons()
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(self.instructions_font)
        label.resize(self.size())
        label.show()

    def display_continue_button(self):
        """Display a continue button."""
        self.block_silent = False
        button = QPushButton(self.instructions[1], self)
        button.resize(button.sizeHint())
        button.clicked.connect(self._trial)
        x = round((self.frameGeometry().width() - button.width()) / 2)
        y = self.frameGeometry().height() - (button.height() + 20)
        button.move(x, y)
        button.show()

    def display_instructions_with_continue_button(self, message):
        """A simple wrapper around the previous two functions."""
        self.display_instructions(message)
        self.display_continue_button()

    def display_countdown_message(self, t=5, s=.1):
        """Display the countdown timer."""
        for i in range(t):
            self.display_instructions(self.instructions[0] % (t - i))
            self.sleep(s)

    def load_image(self, s):
        """Returns a QLabel containing the image `s`. It is possibly important to
        explicitly set the size of the label after setting its pixmap since it does not
        inherit this attribute automatically, even if the entire pixmap is visible.

        """
        label = QLabel(self)
        pixmap = QPixmap(self.vis_stim_paths[s])
        label.setPixmap(pixmap)
        label.resize(pixmap.size())
        label.hide()
        return label

    def move_widget(self, widget, pos):
        """Move a widget to a new position and show it. Returns the new widget geometry.

        """
        x = self.frameGeometry().center().x() + pos[0]
        y = self.frameGeometry().center().y() - pos[1]
        point = QPoint(x, y)
        g = widget.frameGeometry()
        g.moveCenter(point)
        widget.move(g.topLeft())
        return g

    def display_image(self, s, pos=None):
        """Given a label or name of stimulus, show an image on the screen."""
        if isinstance(s, str):
            label = self.load_image(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)

        label.show()
        return label

    def load_text(self, s):
        """Returns a QLabel containing the test `s` in the default font."""
        label = QLabel(s, self)
        label.setFont(self.instructions_font)
        label.setAlignment(Qt.AlignCenter)
        label.resize(label.sizeHint())
        label.hide()
        return label

    def display_text(self, s, pos=None):
        """Given a label or message, show an image on the screen."""
        if isinstance(s, str):
            label = self.load_text(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        return label

    def load_keyboard_arrow_keys(self, lc="", rc="", ypos=-225, text=True):
        """Load left and right arrow keys."""
        l = self.load_image(f"l{lc}.png")
        self.move_widget(l, (-75, ypos))
        l.hide()
        r = self.load_image(f"r{rc}.png")
        self.move_widget(r, (75, ypos))
        r.hide()
        if text:
            a = self.load_text(self.instructions[2])
            self.move_widget(a, (-75, ypos - 75))
            a.hide()
            b = self.load_text(self.instructions[3])
            self.move_widget(b, (75, ypos - 75))
            b.hide()
            return l, r, a, b
        else:
            return l, r

    def display_keyboard_arrow_keys(self, lc="", rc="", ypos=-225, text=True):
        """Draw left and right arrow keys."""
        widgets = self.load_keyboard_arrow_keys(lc, rc, ypos, text)
        [w.show() for w in widgets]
        return widgets

    def next_trial(self):
        """Just a wrapper around _step()"""
        self.vprint('trial results:', self.data.current_trial_details)
        self._step()

    def _step(self):
        """Step forward in the test. This could mean displaying instructions at the
        start of a block, starting the next trial, or continuing to the next test.

        """
        self.vprint("--- stepping forward (test done = %s) ---" % self.data.test_done)

        if self.data.current_trial_details and not self.timed_out:
            self.data.results.append(self.data.current_trial_details)
            self.vprint("previous trial to appended to results")

        if self.data.test_done is True:
            self.vprint("this test is done")
            self.continue_to_next_test()

        else:
            if self.data.control is None:
                self.vprint("this is the first trial; generating control list")
                self.data.control = self.gen_control()

            # grab details of current trial from control list
            self.data.current_trial_details = self.data.control.pop(0)
            self.vprint("this trial has the details:", self.data.current_trial_details)

            # figure out if this is the first trial in a new block
            n = self.data.current_trial_details["trial"]
            self.data.first_trial = n == 0

            if self.data.first_trial is True:

                self.vprint("this is the first trial in a block")
                self._block()

            else:

                self._trial()

    def _block(self):
        """Runs at the start of a new block of trials. Typically this is used to give
        the proband a break or display new instructions.

        """
        self.show_mouse()
        self.timed_out = False
        self.doing_trial = False
        print('timed_out set to False, doing_trial set to False')
        self._stop_block_timeout()
        self.block()
        if self.block_silent:
            self.skip_countdowns = True
            self._trial()

    def _trial(self):
        """Runs at the start of a new trial. Displays the countdown if first in a new
        block, checks if very last trial, flags the fact that a trial is in progress,
        updates the results list.

        """
        if len(self.data.control) == 0:

            self.vprint("test_done set to True")
            self.data.test_done = True

        if self.data.first_trial:

            try:
                if self.data.current_trial_details['block_type'] != 'practice':
                    self.vprint("displaying countdown")
                    self.display_countdown_message()
            except KeyError:
                if not self.skip_countdowns:
                    self.display_countdown_message()

            if self.block_max_time:
                self.vprint('block_max_time = %i s' % self.block_max_time)
                self._start_block_timeout()

        self.doing_trial = True
        self.vprint('doing_trial set to True')
        self.repaint()
        self.trial()

    def _start_block_timeout(self):
        """Initialise a timer which automatically ends the block after time elapses."""
        t = self.block_timeout_timer  # just to make the following more readable
        try:
            t.timeout.disconnect()
            self.vprint("disconnecting timeout")
        except TypeError:
            pass
        t.timeout.connect(self._end_block_early)
        self.vprint("connecting timeout")
        t.start(self.block_max_time * 1000)
        self.vprint("timer started")

    def _stop_block_timeout(self):
        """Stop the timer."""
        if self.block_timeout_timer.isActive():
            self.block_timeout_timer.stop()

    def _end_block_early(self):
        """Remove the rest of the trials from the control list corresponding
        to the current block.

        """
        self.vprint("block timeout occurred")
        current_trial = self.data.current_trial_details
        a = len(self.data.control)

        # removing trials
        if "block" in current_trial.keys():
            b = current_trial["block"]
            self.data.control = [t for t in self.data.control if t["block"] != b]
        else:
            self.data.control = []

        b = len(self.data.control)
        self.vprint(f"control list went from length {a} to {b}")

        # special if this is the end of test
        if len(self.data.control) == 0:
            self.vprint("test_done set to True")
            self.data.test_done = True

        self.timed_out = True
        self.vprint("timed_out set to True")
        self._step()

    def _summarise(self):
        """Preamble to summarise that prevents KeyErrors if no data has been
        recorded (e.g., the subject was completely unresponsive and the task
        timed out.

        """
        self.vprint("calculating test summary based on these data:")
        self.vprint("    ", self.data.results)
        try:
            summary = self.summarise()
            self.vprint("summary:", summary)
            return summary
        except KeyError as k:
            self.vprint(f"couldn't find {k}, probably test timed out")
            return {}
        except IndexError as err:
            self.vprint(f"{err}, probably test timed out")
            return {}

    def block(self):
        """Override this method."""
        pass

    def trial(self):
        """Override this method."""
        pass

    def summarise(self):
        """Override this method."""
        return {}

    def make_zones(self, rects, reset=True):
        """Clickable zones are rects in which mousePressEvents should be registered.

        """
        if reset:
            self.zones = []
        for rect in rects:
            self.zones.append(rect)

    def continue_to_next_test(self):
        """Move on to the next test. This is a wrapper for a parent method
        because some tests have additional stopping rules and I don't want to
        have to call parent().

        """
        self.data.summary.update(self._summarise())
        self.parent().set_central_widget()

    def clear_screen(self):
        """Same as delete_labels().

        """
        self.delete_labels_and_buttons(False)

    def hide_mouse(self):
        self.setCursor(Qt.BlankCursor)

    def show_mouse(self):
        self.setCursor(Qt.ArrowCursor)
