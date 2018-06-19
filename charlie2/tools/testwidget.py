from .data import Data
from .paths import get_vis_stim_paths, get_aud_stim_paths, get_instructions
from .procedure import SimpleProcedure
from PyQt5.QtCore import QTime, Qt, QTimer, QEventLoop, QPoint
from PyQt5.QtGui import QPalette, QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QDesktopWidget


class BaseTestWidget(QWidget):
    def __init__(self, parent=None):
        """Base class for test widgets.

        This is not called directly, but contains methods which are inherited by all
        tests which between them do much of the heavy lifting regarding running tests,
        storing the data, and so on.

        """
        super(BaseTestWidget, self).__init__(parent)
        self.args = self.parent().args
        self.vprint = print if self.args.verbose else lambda *a, **k: None

        # set some default values
        self.setFocusPolicy(Qt.StrongFocus)  # required to accept keyboard events
        self.block_silent = False  # pause between blocks of trials
        self.skip_countdown = False  # count down from 5 before a block
        self.show_mouse()  # show the mouse inside the window
        t = self.args.test_name
        self.vis_stim_paths = get_vis_stim_paths(t)  # paths to visual stimuli
        self.aud_stim_paths = get_aud_stim_paths(t)  # paths to auditory stimuli
        l = self.args.language
        self.instructions = get_instructions(t, l)  # load instructions
        self.instructions_font = QFont("Helvetica", 24)  # big and legible
        self.block_max_time = None  # blocks do not time out
        self.zones = []  # initialise empty "zones" list
        self.trial_on = False  # not currently doing a trial
        self.save_after_each_trial = True  # not sure when I would want to turn this off

        # create timers
        self.test_time = QTime()
        self.block_time = QTime()
        self.trial_time = QTime()
        self.test_time.start()
        self.block_time.start()
        self.trial_time.start()
        self.block_timeout_timer = QTimer()
        self.trial_timeout_timer = QTimer()

        # generate a new list of trials; may not use them
        self.args.remaining_trials = self._make_trials()
        self.args.procedure = self._procedure()

        # instantiate a data object
        self.data = Data(**vars(self.args))

        # begin trials
        # self._step()

    def _make_trials(self):
        trials = self.make_trials()
        assert trials, 'make_trials() must be overridden'
        return trials

    def make_trials(self):
        """Override this method."""
        pass

    def _procedure(self):
        """Override this method."""
        return SimpleProcedure

    def sleep(self, t):
        """PyQt-friendly sleep function."""
        self.vprint("sleeping for %i s" % t)
        self.vprint("during this time, regular quits are blocked")
        trial_was_on = False
        if self.trial_on is True:
            trial_was_on = True
        if trial_was_on:
            self.trial_on = False
        self.parent().ignore_close_event = True
        loop = QEventLoop()

        def f():
            if trial_was_on:
                self.trial_on = True
            loop.quit()

        QTimer.singleShot(t * 1000, f)
        loop.exec_()
        self.parent().ignore_close_event = False

    def hide_labels_and_buttons(self, delete=False):
        """Hide and optionally delete all child label and button widgets. I don't think
        any other kind of widget needs to be deleted/hidden.

        """
        for obj in self.children():
            if isinstance(obj, QLabel) or isinstance(obj, QPushButton):
                self.vprint("hiding", obj)
                obj.hide()
                if delete:
                    print("also deleting it")
                    obj.deleteLater()

    def display_instructions(self, message):
        """Display a set of instructions on the screen."""
        self.vprint('displaying the following message:')
        self.vprint("\n   ", message, "\n")
        self.hide_labels_and_buttons(True)
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(self.instructions_font)
        label.resize(self.size())
        label.show()

    def display_continue_button(self):
        """Display a continue button."""
        self.vprint('displaying the continue button')
        self.block_silent = False  # TODO: Do I need this?
        button = QPushButton(self.instructions[1], self)
        button.resize(button.sizeHint())
        button.clicked.connect(self._trial)
        x = (self.frameGeometry().width() - button.width()) // 2
        y = self.frameGeometry().height() - (button.height() + 20)
        button.move(x, y)
        button.show()

    def display_instructions_with_continue_button(self, message):
        """A simple wrapper around the previous two functions."""
        self.display_instructions(message)
        self.display_continue_button()
        self.vprint("now waiting for continue button to be pressed")

    def _display_countdown(self, t=5, s=.1):
        """Display the countdown timer."""
        self.vprint("displaying the countdown timer")
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

    def load_keyboard_arrow_keys(self, instructions, y=-225):
        """Load keyboard arrow keys and optionally labelling text to be displayed
        underneath. `instructions` must be an iterable of length 2 or 3. The length
        determines how many arrow keys to draw. If any elements are set to None no label
        is displayed.

        """
        w = []
        lx = -75
        rx = 75
        if len(instructions) == 3:
            lx = -225
            rx = 225
        l = self.load_image("l.png")
        self.move_widget(l, (lx, y))
        l.hide()
        w.append(l)
        r = self.load_image("r.png")
        self.move_widget(r, (rx, y))
        r.hide()
        w.append(r)
        xs = [lx, rx]
        if len(instructions) == 3:
            d = self.load_image("d.png")
            self.move_widget(d, (0, y))
            d.hide()
            w.append(d)
            xs = [lx, 0, rx]
        for x, instr in zip(xs, instructions):
            if instr is not None:
                a = self.load_text(instr)
                self.move_widget(a, (x, y - 75))
                a.hide()
                w.append(a)
        return w

    def display_keyboard_arrow_keys(self, instructions, y=-225):
        """Draw left and right arrow keys."""
        widgets = self.load_keyboard_arrow_keys(self, instructions, y)
        [w.show() for w in widgets]
        return widgets

    def next_trial(self):
        """Just a wrapper around _step()"""
        if self.save_after_each_trial:
            self.data.save()
        self._step()

    def _step(self):
        """Step forward in the test. This could mean displaying instructions at the
        start of a block, starting the next trial, or continuing to the next test.

        """
        self.vprint("stepping forward in test")
        try:
            next(self.data.proc)

            if self.data.proc.current_trial.first_trial_in_block:
                self.vprint("this is the first trial in a new block")
                self._block()

            else:
                self.vprint("this is a regular trial")
                self._trial()

        except StopIteration:

            self.vprint("this test is over, moving on to next test")
            self.safe_close()

    def safe_close(self):
        """Abort the procedure if not completed and save."""
        self.vprint("called safe_close()")
        self._stop_block_timeout()
        if not self.data.proc.test_completed:
            self.vprint("aborting")
            self.data.proc.abort()
        summary = self.summarise()
        self.vprint('summary looks like this:')
        self.vprint('   ', summary)
        self.data.summary.update(summary)
        self.data.save()
        self.parent().switch_central_widget()

    def _block(self):
        """Runs at the start of a new block of trials. Typically this is used to give
        the proband a break or display new instructions.

        """
        self.trial_on = False
        self._stop_block_timeout()

        if self.block_silent:
            self.vprint('this is a silent block')
            self.skip_countdown = True
            self.vprint('running _trial()')
            self._trial()

        else:
            self.show_mouse()
            self.vprint('this is a not a silent block')
            self.vprint('running user-defined block()')
            self.block()

    def _trial(self):
        """Runs at the start of a new trial. Displays the countdown if first in a new
        block, checks if very last trial, flags the fact that a trial is in progress,
        updates the results list.

        """
        if self.stopping_rule():
            self.vprint('stopping rule failed')
            self.data.proc.skip_block()
            self.vprint('skipping block in procedure')
            self.vprint('going back to _step()')
            self._step()

        self.vprint('now starting the actual trial')

        if not self.skip_countdown:
            if self.data.proc.current_trial.first_trial_in_block:
                self.vprint('countdown requested')
                self._display_countdown()
                if self.block_max_time:
                    self._start_block_timeout()

        self.trial_on = True
        self.vprint("doing_trial set to True")
        self.repaint()
        self.trial()

    def _start_block_timeout(self):
        """Initialise a timer which automatically ends the block after time elapses."""
        try:
            self.block_timeout_timer.timeout.disconnect()
            self.vprint("disconnecting block timeout timer")
        except TypeError:
            self.vprint("block timeout timer wasn't connected to anything")
            pass
        self.block_timeout_timer.timeout.connect(self._end_block_early)
        self.vprint("connected block timeout timer")
        self.block_timeout_timer.start(self.block_max_time * 1000)
        self.vprint("block timeout timer started")

    def _stop_block_timeout(self):
        """Stop the block timeout timer."""
        if self.block_timeout_timer.isActive():
            self.vprint('stopping the block timeout timer')
            self.block_timeout_timer.stop()
        else:
            self.vprint("requested to stop the block timeout timer, but wasn't not on")

    def _end_block_early(self):
        """End the block early."""
        self.vprint('block timed out')
        self.data.proc.skip_block()
        self.vprint('skipping block in procedure')
        self.vprint('going back to _step()')
        self._step()

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

    def clear_screen(self, delete=False):
        """Wrapper around hide_labels_and_buttons."""
        self.hide_labels_and_buttons(delete)

    def hide_mouse(self):
        self.setCursor(Qt.BlankCursor)

    def show_mouse(self):
        self.setCursor(Qt.ArrowCursor)

    def stopping_rule(self):
        """Override this method."""
        return False

    def begin(self):
        self._step()
