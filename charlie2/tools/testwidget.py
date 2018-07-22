from copy import copy
from logging import getLogger
from .data import SimpleProcedure
from .paths import get_vis_stim_paths, get_aud_stim_paths, get_instructions
from .google_drive import backup
from PyQt5.QtCore import QTime, Qt, QTimer, QEventLoop, QPoint
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from httplib2 import ServerNotFoundError


logger = getLogger(__name__)


class BaseTestWidget(QWidget):
    def __init__(self, parent=None):
        """Base class for test widgets.

        This is not called directly, but contains methods which are inherited by all
        tests which between them do much of the heavy lifting regarding running tests,
        storing data, and so on.

        """
        super(BaseTestWidget, self).__init__(parent)
        logger.info("test widget created")
        logger.info("transferring command-line arguments from mainwidget to testwidget")
        self.kwds = self.parent().kwds

        self.vis_stim_paths = get_vis_stim_paths(self.kwds["test_name"])
        self.aud_stim_paths = get_aud_stim_paths(self.kwds["test_name"])
        self.feedback_sounds = []
        self.instructions_font = QFont("Helvetica", 26)
        self.test_time = QTime()
        self.block_time = QTime()
        self.trial_time = QTime()
        self.silent_block = False
        self.skip_countdown = False
        self.test_deadline = None
        self.block_deadline = None
        self.trial_deadline = None
        self.test_timer = QTimer()
        self.test_timer.setSingleShot(True)
        self.block_timer = QTimer()
        self.block_timer.setSingleShot(True)
        self.block_timer.timeout.connect(self._block_timeout)
        self.trial_timer = QTimer()
        self.trial_timer.setSingleShot(True)
        self.trial_timer.timeout.connect(self._trial_timeout)
        self.zones = []
        self.instructions = get_instructions(
            self.kwds["test_name"], self.kwds["language"]
        )
        self.data = None
        self.setFocusPolicy(Qt.StrongFocus)

        self._performing_block = False
        self._performing_trial = False
        self._mouse_visible = True

    def begin(self):
        """Start the test."""
        logger.info("initialising a data object")
        self.data = SimpleProcedure(**self.kwds)
        logger.info("checking if test was resumed")
        if not self.data.data["test_resumed"]:
            logger.info("answer is False, so populating the remaining_trials list")
            self.data.data["remaining_trials"] = self.make_trials()
        logger.info("initialising the test timer")
        self.test_time.start()
        self._step()

    def _step(self):
        """Step forward in the test. This could mean displaying instructions at the
        start of a block, starting the next trial, or continuing to the next test.

        """
        logger.info("stepping forward in test")

        logger.info("testing stopping rule")
        if len(self.data.data["completed_trials"]) > 0:
            if self._block_stopping_rule():
                self._block_stop()
        else:
            logger.info("no trials yet completed, so skipping stopping rule")

        logger.info("trying to iterate procedure")
        try:
            next(self.data)
            logger.info("successfully iterated")
            logger.info("checking if this is first trial in a new block")
            if self.data.data["current_trial"].first_trial_in_block:
                logger.info("yes, running _block()")
                self._block()
            else:
                logger.info("no, running _trial()")
                self._trial()

        except StopIteration:
            logger.warning("failed to iterate (hopefully) bc this is end of test")
            self.safe_close()

    def make_trials(self):
        """Override this method."""
        raise AssertionError("make_trials must be overridden")

    def _block(self):
        """Runs at the start of a new block of trials. Typically this is used to give
        the proband a break or display new instructions."""
        self._performing_block = False
        logger.info("checking if this is a silent block")
        if self.silent_block:
            logger.info("this is indeed a silent block")
            logger.info("skipping the countdown")
            self.skip_countdown = True
            logger.info("running _trial()")
            self._trial()
        else:
            logger.info("this is a not a silent block")
            logger.info("running block()")
            self.block()

    def block(self):
        """Override this method."""
        raise AssertionError("block must be overridden")

    def _trial(self):
        """Runs at the start of a new trial. Displays the countdown if first in a new
        block, checks if very last trial, flags the fact that a trial is in progress,
        updates the results list."""
        logger.info("called _trial()")
        t = self.data.data["current_trial"]
        logger.info("current trial looks like %s" % str(dict(t)))
        if t.first_trial_in_block and not self.skip_countdown:
            logger.info("countdown requested")
            self._display_countdown()
        self.repaint()
        if self.data.data["current_trial"].first_trial_in_block is True:
            logger.info("this is the first trial in a new block")
            self.performing_block = True
        self.performing_trial = True
        self.trial()

    def safe_close(self):
        """Safely clean up and save the data at the end of the test."""
        logger.info("called safe_close()")
        if self.data.data["test_completed"] is True:
            logger.info("saving a csv of the completed trials")
            self.data.save_completed_trials_as_csv()
            logger.info("trying to summarise performance on the test")
            summary = self.summarise()
            logger.info("updating data object to include summary")
            self.data.data["summary"] = summary
            self.data.save()
            logger.info("saving the summary")
            self.data.save_summary()
        else:
            self.data.save()
            logger.info("no trials completed, so don't try to summarise")
        logger.info("all done, so switching the central widget")
        self.parent().switch_central_widget()

    @property
    def performing_trial(self):
        return self._performing_trial

    @performing_trial.setter
    def performing_trial(self, value):
        assert isinstance(value, bool), "performing_trial must be a bool"
        self._performing_trial = value
        time = self.trial_time
        timer = self.trial_timer
        deadline = self.trial_deadline
        if timer.isActive():
            logger.info("stopping trial timer")
            timer.stop()
        if value is True:
            logger.info("performing_trial set to True")
            logger.info("starting the trial time")
            time.start()
        if value is True and deadline:
            logger.info("trial deadline: %s" % str(self.trial_deadline))
            logger.info("starting one-shot trial timer")
            timer.start(deadline)

    @property
    def performing_block(self):
        return self._performing_block

    @performing_block.setter
    def performing_block(self, value):
        assert isinstance(value, bool), "performing_block must be a bool"
        self._performing_block = value
        time = self.block_time
        timer = self.block_timer
        deadline = self.block_deadline
        if timer.isActive():
            logger.info("stopping block timer")
            timer.stop()
        if value is True:
            logger.info("performing_block set to True")
            logger.info("starting the block time")
            time.start()
        if value is True and deadline:
            logger.info("block deadline: %s" % str(self.block_deadline))
            logger.info("starting one-shot block timer")
            timer.start(deadline)

    @property
    def mouse_visible(self):
        return self._mouse_visible

    @mouse_visible.setter
    def mouse_visible(self, value):
        assert isinstance(value, bool), "mouse_visible must be a bool"
        if value is False:
            self.setCursor(Qt.BlankCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self._mouse_visible = value

    def trial(self):
        """Override this method."""
        raise AssertionError("trial must be overridden")

    def summarise(self):
        """Override this method."""
        raise AssertionError("summarise must be overridden")

    def mousePressEvent_(self, event):
        """Override this method."""
        pass

    def keyReleaseEvent_(self, event):
        """Override this method."""
        pass

    def sleep(self, t):
        """Sleep for `t` ms.

        Use instead of `time.sleep()` or any other method of sleeping because (a) Qt
        handles it properly and (b) it prevents a `closeEvent` from quitting the test
        during this time.

        Args:
            t (float): Time to sleep in seconds.

        """
        logger.info("sleeping for %i s" % t)
        self.parent().ignore_close_event = True
        loop = QEventLoop()
        QTimer.singleShot(t, loop.quit)
        loop.exec_()
        self.parent().ignore_close_event = False

    def display_instructions(self, message, font=None):
        """Display instructions.

        This method will first hide any visible widgets (e.g., images from the last
        trial). Typically `message` is an item from the list `self.instructions`.

        Args:
            message (str): Message to display.
            font (:obj:`QFont`, optional): A font in which to display the instructions.

        Returns:
            label (QLabel): Object containing the message.

        """
        logger.info("displaying the following message:" + message.replace("\n", " "))
        self.clear_screen()
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        if font is None:
            label.setFont(self.instructions_font)
        else:
            label.setFont(font)
        label.resize(self.size())
        label.show()
        return label

    def display_instructions_with_continue_button(self, message, font=None):
        """Display instructions with a continue button.

        This is the same as `self.display_instructions` except that a continue button is
        additionally displayed. Continue buttons prevent the test from moving forward
        until pressed. Generally this is used at the beginning of blocks of trials.

        Args:
            message (str): Message to display.
            font (:obj:`QFont`, optional): A font in which to display the instructions.

        Returns:
            label (QLabel): Object containing the message.
            button (QPushButton): Button.

        """
        label = self.display_instructions(message, font)
        button = self._display_continue_button()
        logger.info("now waiting for continue button to be pressed")
        return label, button

    def display_instructions_with_space_bar(self, message):
        """Display instructions, allowing the space bar to continue.

        Args:
            message (str): Message to display.

        Returns:
            label (QLabel): Object containing the message.

        """
        label = self.display_instructions(message)
        logger.info("now waiting for space bar to be pressed")
        self._keyReleaseEvent = copy(self.keyReleaseEvent)
        self.keyReleaseEvent = self._space_bar_continue
        label.setFocus()
        logger.debug("what widget needs to be in focus for this to work?")
        logger.debug("self? %s" % self.hasFocus())
        logger.debug("label? %s" % label.hasFocus())
        return label

    def _space_bar_continue(self, event):
        logger.info("%s pressed, looking for %s" % (event.key(), Qt.Key_Space))
        if event.key() == Qt.Key_Space:
            logger.debug("got the correct key")
            self._trial()
            self.keyReleaseEvent = self._keyReleaseEvent

    def load_image(self, s):
        """Return an image.

        It is possibly important for correct alignment to explicitly set the size of the
        label after setting its pixmap since it does not inherit this attribute even
        though the entire pixmap may br visible.

        Args:
            s (str): Path to the .png image file.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        label = QLabel(self)
        pixmap = QPixmap(self.vis_stim_paths[s])
        label.setPixmap(pixmap)
        label.resize(pixmap.size())
        label.hide()
        return label

    def move_widget(self, widget, pos):
        """Move `widget` to new coordinates.

        Coords are relative to the centre of the window where (1, 1) would be the upper
        right.

        Args:
            widget (QWidget): Any widget.
            pos (:obj:`tuple` of :obj:`int`): New position.

        Returns:
            g (QRect): Updated geometry of the wdiget.

        """
        x = self.frameGeometry().center().x() + pos[0]
        y = self.frameGeometry().center().y() - pos[1]
        point = QPoint(x, y)
        g = widget.frameGeometry()
        g.moveCenter(point)
        widget.move(g.topLeft())
        return g

    def display_image(self, s, pos=None):
        """Show an image on the screen.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Path to image or an image itself.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords of image.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        if isinstance(s, str):
            label = self.load_image(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        logger.info("showing %s" % s)
        return label

    def load_text(self, s):
        """Return a QLabel containing text.

        Args:
            s (str): Text.

        Returns:
            label (QLabel): Label containing the text.

        """
        label = QLabel(s, self)
        label.setFont(self.instructions_font)
        label.setAlignment(Qt.AlignCenter)
        label.resize(label.sizeHint())
        label.hide()
        return label

    def display_text(self, s, pos=None):
        """Same as `load_text` but also display it.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Text or label containing text.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords.

        Returns:
            label (QLabel): Label containing the text.

        """
        if isinstance(s, str):
            label = self.load_text(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        return label

    def load_keyboard_arrow_keys(self, instructions, y=-225):
        """Load keyboard arrow keys.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

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
        """Same as `load_keyboard_arrow_keys` except also show them.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

        """
        widgets = self.load_keyboard_arrow_keys(instructions, y)
        [w.show() for w in widgets]
        return widgets

    def make_zones(self, rects, reset=True):
        """Update `self.zones`.

        `self.zones` contains areas of the window (`QRect` objects) that can be pressed.

        Args:
            rects (:obj:`list` of :obj:`QRect`): List of `QRects`.
            reset (:obj:`bool`, optional): Remove old items.

        """
        if reset:
            self.zones = []
        for rect in rects:
            self.zones.append(rect)

    def clear_screen(self, delete=False):
        """Hide widgets.

        Hides and optionally deletes all children of this widget.

        Args:
            delete (:obj:`bool`, optional): Delete the widgets as well.

        """
        # for widgets  organized in a layout
        if self.layout() is not None:
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    if delete:
                        widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        # for widgets not organized
        for widget in self.children():
            if hasattr(widget, "hide"):
                widget.hide()
            if delete:
                widget.deleteLater()

    def basic_summary(self, **kwds):
        """Returns an basic set of summary statistics.

        Returns:
            dic (dict): dictionary of results.

        """
        logger.info("called basic_summary()")
        if "trials" not in kwds:
            total_trials = self.data.data["completed_trials"]
        else:
            total_trials = kwds["trials"]
        total_trials = [t for t in total_trials if not t["practice"]]
        completed_trials = [t for t in total_trials if t["status"] == "completed"]
        skipped_trials = [t for t in total_trials if t["status"] == "skipped"]
        first_trial = total_trials[0]

        dic = {
            "total_trials": len(total_trials),
            "completed_trials": len(completed_trials),
            "skipped_trials": len(skipped_trials),
        }

        try:

            correct_trials = [t for t in completed_trials if t["correct"]]
            rt_correct_ms = [t["trial_time_elapsed_ms"] for t in correct_trials]
            dic["correct_trials"] = len(correct_trials)

            if len(completed_trials) > 0:

                dic["accuracy"] = len(correct_trials) / len(completed_trials)

            if len(completed_trials) > 0 and len(correct_trials) > 0:

                last_trial = completed_trials[-1]
                dic["began_timestamp"] = str(first_trial["timestamp"])
                dic["duration_ms"] = last_trial["block_time_elapsed_ms"]
                dic["total_duration_ms"] = last_trial["test_time_elapsed_ms"]
                dic["finished_timestamp"] = str(last_trial["timestamp"])
                dic["mean_rt_correct_ms"] = sum(rt_correct_ms) / len(rt_correct_ms)

                if "adjust" in kwds:
                    all_rts = [t["trial_time_elapsed_ms"] for t in completed_trials]
                    mean_rt = sum(all_rts) / len(all_rts)
                    est_extra_time = mean_rt * len(skipped_trials)
                    dic["duration_ms_adjusted"] = dic["duration_ms"] + est_extra_time
            else:

                dic["began_timestamp"] = None
                dic["duration_ms"] = None
                dic["total_duration_ms"] = None
                dic["finished_timestamp"] = None
                dic["mean_rt_correct_ms"] = 0

                if "adjust" in kwds:
                    dic["duration_ms_adjusted"] = None

        except KeyError:

            if len(completed_trials) > 0:

                last_trial = completed_trials[-1]
                dic["began_timestamp"] = str(first_trial["timestamp"])
                dic["duration_ms"] = last_trial["block_time_elapsed_ms"]
                dic["total_duration_ms"] = last_trial["test_time_elapsed_ms"]
                dic["finished_timestamp"] = str(last_trial["timestamp"])

            else:

                dic["began_timestamp"] = None
                dic["duration_ms"] = None
                dic["total_duration_ms"] = None
                dic["finished_timestamp"] = None
                dic["mean_rt_correct_ms"] = 0

        if "prefix" in kwds:
            p = kwds["prefix"] + "_"
            dic = {p + k: v for k, v in dic.items() if k != "total_duration_ms"}

        return dic

    def _display_continue_button(self):
        """Display a continue button."""
        logger.info("displaying the continue button")
        button = QPushButton(self.instructions[1], self)
        button.setFont(self.instructions_font)
        size = (button.sizeHint().width() + 20, button.sizeHint().height() + 20)
        button.resize(*size)
        button.clicked.connect(self._continue_button_pressed)
        x = (self.frameGeometry().width() - button.width()) // 2
        y = self.frameGeometry().height() - (button.height() + 20)
        button.move(x, y)
        button.show()
        return button

    def display_trial_continue_button(self):
        """The button is connected to _next_trial instead of _trial."""
        button = self._display_continue_button()
        button.clicked.disconnect()
        button.clicked.connect(self._next_trial)

    def _continue_button_pressed(self):
        logger.info("continue button was pressed")
        self._trial()

    def _display_countdown(self, t=5, s=1000):
        """Display the countdown timer."""
        logger.info("displaying the countdown timer")
        for i in range(t):
            self.display_instructions(self.instructions[0] % (t - i))
            self.sleep(s)

    @property
    def _test_time_left(self):
        if self.test_deadline:
            return self.test_deadline - self.test_time.elapsed()
        else:
            return None

    @property
    def _test_time_up(self):
        if self._test_time_left:
            return self._test_time_left <= 0

    @property
    def _block_time_left(self):
        if self.block_deadline:
            return self.block_deadline - self.block_time.elapsed()
        else:
            return None

    @property
    def _block_time_up(self):
        if self._block_time_left:
            return self._block_time_left <= 0

    @property
    def _trial_time_left(self):
        if self.trial_deadline:
            return self.trial_deadline - self.trial_time.elapsed()
        else:
            return None

    @property
    def _trial_time_up(self):
        if self._trial_time_left:
            return self._trial_time_left <= 0

    def _add_timing_details(self):
        """Gathers some details about the current state from the various timers."""
        logger.info("adding timing details to current_trial")
        dic = {
            "test_time_elapsed_ms": self.test_time.elapsed(),
            "block_time_elapsed_ms": self.block_time.elapsed(),
            "trial_time_elapsed_ms": self.trial_time.elapsed(),
            "test_time_left_ms": self._test_time_left,
            "block_time_left_ms": self._block_time_left,
            "trial_time_left_ms": self._trial_time_left,
            "test_time_up_ms": self._test_time_up,
            "block_time_up_ms": self._block_time_up,
            "trial_time_up_ms": self._trial_time_up,
        }
        self.data.data["current_trial"].update(dic)

    def mousePressEvent(self, event):
        """Overridden from `QtWidget`."""
        logger.info("mouse press event occurred, so checking if performing a trial")
        logger.info("answer is %s" % str(self.performing_trial))
        if self.performing_trial:
            self.mousePressEvent_(event)
            self._add_timing_details()
            t = self.data.data["current_trial"]
            if t.status == "completed":
                logger.info("current_trial was completed successfully")
                logger.info("(final version) of current_trial looks like %s" % str(t))
                # if t.practice is True:
                #     self.play_feedback_sound(t.correct)
                self._next_trial()

    def keyReleaseEvent(self, event):
        """Overridden from `QtWidget`."""
        logger.info("mouse press event occurred, so checking if performing a trial")
        logger.info("answer is %s" % str(self.performing_trial))
        if self.performing_trial:
            self.keyReleaseEvent_(event)
            self._add_timing_details()
            t = self.data.data["current_trial"]
            if self.data.data["current_trial"].status == "completed":
                logger.info("current_trial was completed successfully")
                logger.info("(final version) of current_trial looks like %s" % str(t))
                # if t.practice is True:
                #     self.play_feedback_sound(t.correct)
                self._next_trial()

    def _next_trial(self):
        """Moves on to the next trial."""
        self.performing_trial = False
        logger.info("called _next_trial()")
        logger.info("saving a csv of the completed trials")
        self.data.save_completed_trials_as_csv()
        self._step()

    def next_trial(self):
        self._next_trial()

    def _trial_timeout(self):
        """End a trial early because it had timed out."""
        logger.info("timing out the current trial")
        self.data.skip_current_trial("timeout")
        self._next_trial()

    def _block_timeout(self):
        """End a trial early because it had timed out."""
        logger.info("timing out the current block")
        self.data.skip_current_block("timeout")
        self._next_trial()

    def _block_stopping_rule(self):
        """This is a little complicated. Because `self.data.data["completed_trials"]`
        gets updated when the data object is iterated, the old trial does not get
        appended to this list until the next one has already started. Stopping rules
        should be called before this iteration, yet should evaluate all completed
        trials. Therefore we temporarily edit completed_trials to include current_trial
        (actually the old trial, but we are in-between trials at this point). This
        is almost certainly not the best way to do this, but I don't have the time to
        restructure everything to fix it.

        """
        already_completed = self.data.data["test_completed"]
        if already_completed:
            return False
        if self.data.data["current_trial"] is not None:
            current_trial = dict(self.data.data["current_trial"])
            old_completed_trials = copy(self.data.data["completed_trials"])
            self.data.data["completed_trials"].append(current_trial)
            result = self.block_stopping_rule()
            self.data.data["completed_trials"] = old_completed_trials
        else:
            result = self.block_stopping_rule()
        return result

    def block_stopping_rule(self):
        """Override this method."""
        return False

    def _block_stop(self):
        """End a trial early because stopping rule passed."""
        logger.info("stopping the current block")
        self.data.skip_current_block("stopping rule failed")

    # def _preload_feedback_sounds(self):
    #     """This should prevent lags when playing sounds."""
    #     for name in ["incorrect.wav", "correct.wav"]:
    #         sound = QSoundEffect()
    #         sound.setSource(QUrl.fromLocalFile(self.aud_stim_paths[name]))
    #         self.feedback_sounds.append(sound)
    #
    # def play_feedback_sound(self, correct):
    #     """Play either the correct sound if true or incorrect sound if false."""
    #     self.feedback_sounds[correct].play()
