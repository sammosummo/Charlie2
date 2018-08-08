"""Defines a Qt widget which serves as the blueprint for tests.

"""
from logging import getLogger

from PyQt5.QtCore import QEventLoop, Qt, QTime, QTimer
from PyQt5.QtGui import QMouseEvent, QKeyEvent

from .procedure import SimpleProcedure
from .stats import basic_summary
from .visualwidget import VisualWidget

logger = getLogger(__name__)


class BaseTestWidget(VisualWidget):
    def __init__(self, parent=None) -> None:
        """Base class for test widgets.

        This is not called directly, but contains methods which are inherited by all
        tests. These do much of the heavy lifting regarding running tests, storing data,
        and so on.

        """
        super(BaseTestWidget, self).__init__(parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # timers
        self.block_time = QTime()
        self.block_timer = QTimer()
        self.block_timer.setSingleShot(True)
        self.block_timer.timeout.connect(self._block_timeout)
        self.trial_time = QTime()
        self.trial_timer = QTimer()
        self.trial_timer.setSingleShot(True)
        self.trial_timer.timeout.connect(self._trial_timeout)

        # override these if necessary
        self.silent_block = False
        self.skip_countdown = False
        self.block_deadline = None
        self.trial_deadline = None
        self.procedure = None
        self.current_trial = None

        # silent attributes
        self._performing_block = False
        self._performing_trial = False
        self._mouse_visible = True

        # set focus so we can accept keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    @property
    def performing_block(self) -> bool:
        return self._performing_block

    @performing_block.setter
    def performing_block(self, value) -> None:
        """Block timers will be silently and automatically started or restarted here."""
        assert isinstance(value, bool), "performing_block must be a bool"
        self._performing_block = value
        time = self.block_time
        timer = self.block_timer
        deadline = self.block_deadline
        if timer.isActive():
            logger.debug("stopping block timer")
            timer.stop()
        if value is True:
            logger.debug("performing_block set to True")
            logger.debug("starting the block time")
            time.start()
        if value is True and deadline:
            logger.debug("block deadline: %s" % str(self.block_deadline))
            logger.debug("starting one-shot block timer")
            timer.start(deadline)

    @property
    def performing_trial(self) -> bool:
        return self._performing_trial

    @performing_trial.setter
    def performing_trial(self, value: bool) -> None:
        """Start of a trial defined from when the proband can start making responses.
        Trial timers will be silently and automatically started or restarted here.

        Args:
            value (bool): Are we performing a trial or not?

        """
        assert isinstance(value, bool), "performing_trial must be a bool"
        self._performing_trial = value
        time = self.trial_time
        timer = self.trial_timer
        deadline = self.trial_deadline
        if timer.isActive():
            logger.debug("stopping trial timer")
            timer.stop()
        if value is True:
            logger.debug("performing_trial set to True")
            logger.debug("starting the trial time")
            time.start()
        if value is True and deadline:
            logger.debug("trial deadline: %s" % str(self.trial_deadline))
            logger.debug("starting one-shot trial timer")
            timer.start(deadline)

    @property
    def mouse_visible(self) -> bool:
        return self._mouse_visible

    @mouse_visible.setter
    def mouse_visible(self, value: bool) -> None:
        """Makes the mouse visible or invisible."""
        assert isinstance(value, bool), "mouse_visible must be a bool"
        if value is False:
            self.setCursor(Qt.BlankCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self._mouse_visible = value

    @property
    def _time_left_in_block(self) -> int:
        """Calculates difference between deadline and elapsed."""
        if isinstance(self.block_deadline, int):
            return self.block_deadline - self.block_time.elapsed()
        else:
            return 0

    @property
    def _block_time_up(self) -> bool:
        if isinstance(self._time_left_in_block, int):
            return self._time_left_in_block <= 0
        else:
            return False

    @property
    def _time_left_in_trial(self) -> int:
        """Calculates difference between deadline and elapsed."""
        if isinstance(self.trial_deadline, int):
            return self.trial_deadline - self.trial_time.elapsed()
        else:
            return 0

    @property
    def _trial_time_up(self) -> int:
        if isinstance(self._time_left_in_trial, int):
            return self._time_left_in_trial <= 0
        else:
            return 0

    def begin(self) -> None:
        """Start the test.

        Public method called by the parent widget. Starts by initialising a procedure
        (currently only SimpleProcedure implemented), creates a new trial list if
        needed, and steps into the test.

        """
        logger.debug("called begin()")
        self.procedure = SimpleProcedure(**self.kwds)
        started = self.procedure.data["test_started"]
        completed = self.procedure.data["test_completed"]
        if started is False and completed is False:
            logger.debug("generating new remaining_trials list")
            self.procedure.data["remaining_trials"] = self.make_trials()
            self.procedure.update()
            logger.debug(f"looks like {self.procedure.data['remaining_trials']}")
        self._step()

    def _step(self) -> None:
        """Step forward in the test.

        Private method. This could mean displaying instructions at the start of a block,
        starting the next trial, or continuing to the next test if all trials are done.

        """
        logger.debug("called _step()")

        try:
            self.current_trial = self.procedure.next(self.current_trial)
            logger.debug(f"successfully iterated, got this: {self.current_trial}")

            if self.current_trial.first_trial_in_block:
                logger.debug("first trial in new block")
                self._block()
            else:
                logger.debug("after first trial in new block")
                if self._block_stopping_rule():
                    logger.debug("stopping rule says to stop")
                    self._stop_block()
                else:
                    logger.debug("stopping rule says to go")
                    self._trial()

        except StopIteration:
            logger.info("failed to iterate, end of test")
            self.safe_close()

    def _stop_block(self) -> None:
        """Stop the current block because stopping rule passed."""
        logger.debug("called _block_stop")
        self.procedure.skip_block(
            self.current_trial.block_number, "stopping rule failed"
        )
        self.current_trial.status = "skipped"
        self.current_trial.reason_skipped = "stopping rule failed"
        self._next_trial()

    def _block_stopping_rule(self) -> bool:
        """Apply block stopping rule.

        Private method and a wrapper around the public method of the same name.

        """
        logger.debug("called _block_stopping_rule()")
        return False if self.current_trial is None else self.block_stopping_rule()

    def _block(self) -> None:
        """Runs at the start of a new block of trials.

        Private method. Typically blocks are used to delineate trials of a different
        condition, when new instructions or a break are often needed.

        """
        logger.debug("called _block()")
        self._performing_block = False
        logger.debug("checking if this is a silent block")

        if self.silent_block:
            logger.debug("this is indeed a silent block")
            logger.debug("skipping the countdown")
            self.skip_countdown = True
            logger.debug("running _trial()")
            self._trial()
        else:
            logger.debug("this is a not a silent block")
            self.skip_countdown = False
            logger.debug("running block()")
            self.block()

    def _trial(self) -> None:
        """Runs at the start of a new trial.

        Private method. Displays the countdown if first in a new block, checks if very
        last trial, flags the fact that a trial is in progress, updates the results.

        """
        logger.debug("called _trial()")
        if self.current_trial.first_trial_in_block and not self.skip_countdown:
            logger.debug("countdown requested")
            self.display_countdown()
        self.repaint()
        if self.current_trial.first_trial_in_block is True:
            logger.debug("this is the first trial in a new block")
            self.performing_block = True
        self.performing_trial = True
        self.trial()

    def block_stopping_rule(self) -> bool:
        """Override this method."""
        return False

    def make_trials(self) -> None:
        """Override this method."""
        raise AssertionError("make_trials must be overridden")

    def safe_close(self) -> None:
        """Safely clean up and save the data."""
        logger.debug("called safe_close()")

        # properly ended test
        if self.procedure.data["test_completed"] is True:
            logger.debug("summarising the results")
            self.procedure.data["summary"] = self.summarise()
            self.procedure.save()
            self.procedure.save_summary()

        # early quit
        else:
            logger.warning("quit early, need to save orphaned trial")
            rt = [t for t in self.procedure.data["remaining_trials"]]
            self.procedure.data["remaining_trials"] = [dict(self.current_trial)] + rt
            self.procedure.save()

        # end test
        logger.debug("all done, so switching the central widget")
        self.parent().switch_central_widget()

    def _block_timeout(self) -> None:
        """End a block early because it had timed out."""
        logger.debug("called _block_timeout()")
        self.procedure.skip_block(self.current_trial.block_number, "timeout")
        self._trial_timeout()

    def _trial_timeout(self) -> None:
        """End a trial early because it had timed out."""
        logger.debug("called _trial_timeout()")
        self.current_trial.status = "skipped"
        self.current_trial.reason_skipped = "timeout"
        self._next_trial()

    def _next_trial(self) -> None:
        """Moves on to the next trial."""
        logger.debug("called _next_trial()")
        self.performing_trial = False
        self._step()

    def next_trial(self) -> None:
        """Moves on to the next trial (public version)."""
        logger.debug("called next_trial()")
        self._next_trial()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Overridden from `QtWidget`.

        Args:
            event (PyQt5.QtGui.QMouseEvent):
        """
        logger.debug(f"called mousePressEvent() with event={event}")
        if self.performing_trial:
            self.mousePressEvent_(event)
            self._add_timing_details()
            if self.current_trial.status == "completed":
                logger.debug("current_trial was completed successfully")
                # if t.practice is True:
                #     self.play_feedback_sound(t.correct)
                self._next_trial()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """Overridden from `QtWidget`."""
        logger.debug(f"called keyReleaseEvent() with event={event}")
        if self.performing_trial:
            self.keyReleaseEvent_(event)
            self._add_timing_details()
            if self.current_trial.status == "completed":
                logger.debug("current_trial was completed successfully")
                # if t.practice is True:
                #     self.play_feedback_sound(t.correct)
                self._next_trial()

    def _add_timing_details(self) -> None:
        """Gathers some details about the current state from the various timers."""
        logger.debug("called _add_timing_details()")
        dic = {
            "block_time_elapsed_ms": self.block_time.elapsed(),
            "trial_time_elapsed_ms": self.trial_time.elapsed(),
            "block_time_left_ms": self._time_left_in_block,
            "trial_time_left_ms": self._time_left_in_trial,
            "block_time_up_ms": self._block_time_up,
            "trial_time_up_ms": self._trial_time_up,
        }
        self.current_trial.update(dic)

    def block(self) -> None:
        """Override this method."""
        raise AssertionError("block must be overridden")

    def trial(self) -> None:
        """Override this method."""
        raise AssertionError("trial must be overridden")

    def summarise(self) -> dict:
        """This method can be overridden."""
        return basic_summary(self.procedure.data["completed_trials"])

    def mousePressEvent_(self, event: QMouseEvent) -> None:
        """Override this method."""
        pass

    def keyReleaseEvent_(self, event: QKeyEvent) -> None:
        """Override this method."""
        pass

    def sleep(self, t: int) -> None:
        """Sleep for `t` ms.

        Use instead of `time.sleep()` or any other method of sleeping because (a) Qt
        handles it properly and (b) it prevents a `closeEvent` from quitting the test
        during this time.

        Args:
            t (int): Time to sleep in seconds.

        """
        logger.debug(f"called sleep with t={t}")
        self.parent().ignore_close_event = True
        loop = QEventLoop()
        QTimer.singleShot(t, loop.quit)
        loop.exec_()
        self.parent().ignore_close_event = False
