"""
============
Trail making
============

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/make_trail_trials.py
:Author: Sam Mathias

Description
===========

In this task, the proband must press the circles drawn on the screen in a specified
order, making a 'trail' between them. There are a total of six blocks to the test, with
varying numbers of trials in each block. In the first and second blocks, the proband
draws a trail between consecutive numbers, starting with 1. In the third and fourth
blocks, the proband does the same with letters starting with 'a'. In the fifth and sixth
blocks, the proband alternates between numbers and letters. Odd-numbered blocks are
'practice' blocks with 5 trials each, and even-numbered blocks are 'test' blocks with
20 trials each.

The traditional trail-making test (see [1]_ and [2]_) contains only two blocks
(equivalent to the 'number' and 'number-letter' blocks in the present version). The
traditional test is also done with pen and paper, and requires an experienced
experimenter to administer it. Thus the current version should be more convenient than
the traditional test. Please note that this test has not been verified against the
traditional version, however preliminary data from our studies suggests that they are
correlated.

References
==========

.. [1] Reitan, R. M. (1958). Validity of the Trail Making test as an indicator of
  organic brain damage. Percept Mot Skills, 8, 271-276.

.. [2] Corrigan, J. D., & Hinkeldey, M. S. (1987). Relationships between parts A and B
  of the Trail Making Test. J Clin Psychol, 43(4), 402–409.

"""
from typing import List, Dict

__version__ = 2.0
__author__ = "Sam Mathias"


from logging import getLogger

from PyQt5.QtGui import QPainter, QPen, QMouseEvent

from ..tools.basetestwidget import BaseTestWidget
from ..tools.recipes import make_trail_trials

logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Sets a block deadline of 180 s.
            3. Defines rects and image storage lists.
            4. Defines a blank variable to store the tick.

        """
        super(TestWidget, self).__init__(parent)
        self.block_deadline = 180 * 1000
        self.rects = []
        self.images = []
        self.tick = None

    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        This was complicated to generate and required many manual edits, so was all done
        in a different script and simply imported here.

        Returns:
             :obj:`list`: Each entry is a dict containing:
                1. `block_number` (:obj:`int`)
                2. `block_type` (:obj:`str`)
                3. `trial_number` (:obj:`int`)
                4. `blaze_position` (:obj:`tuple` of :obj:`int`)
                5. `glyph` (:obj:`str`)

        """
        return make_trail_trials()

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays the task instructions with a continue button.
            2. Displays the blazes.
            3. Makes "zones".

        In this test, individual blazes and their press events are considered "trials"
        and the whole visual array is considered a "block".

        """
        b = self.current_trial.block_number
        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # find all trials in this block
        trials = [self.current_trial]  # because first trial was popped
        trials += [t for t in self.procedure.remaining_trials if t["block_number"] == b]

        # get their glyphs and positions
        glyphs = [t["glyph"] for t in trials]
        positions = [t["blaze_position"] for t in trials]

        # load the blazes but don't show them yet
        self.rects = []
        self.images = []
        for glyph, pos in zip(glyphs, positions):
            img = self.display_image(f"a_{glyph}.png", pos)
            self.images.append(img)
            img.hide()
            self.rects.append(img.frameGeometry())

        self.tick = self.display_image("tick.png", positions[0])
        self.tick.hide()

        # make zones
        self.make_zones(self.rects)

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen.
            2. Displays the blazes.
            3. Resets a list for recording time and position of attempts.
            4. Resets "errors" and "attempts" counters.

        """
        self.clear_screen(delete=False)
        t = self.current_trial

        # show the blazes
        if not t.first_trial_in_block:
            [img.show() for img in self.images + [self.tick]]
        else:
            [img.show() for img in self.images]

        # reset click/press counters
        t.attempts = 0
        t.errors = 0
        t.responses_list = []

    def mousePressEvent_(self, event: QMouseEvent) -> None:
        """Mouse or touchscreen press event.

        If the event was within a zone, marks trial as complete and moves on.

        Args:
            event (PyQt5.QtGui.QMouseEvent)

        """
        ix = [event.pos() in z for z in self.zones]
        t = self.current_trial
        if any(ix):
            logger.debug("clicked within a blaze")
            rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = rsp == t.trial_number
            t.responses_list.append((rsp, self.trial_time.elapsed()))

            if t.correct:
                logger.debug("clicked within the correct blaze")
                self.current_trial.status = "completed"
            else:
                logger.debug("clicked within a different blaze")
                t.errors += 1
        else:
            logger.debug("clicked outside a blaze")
            t.attempts += 1
            t.responses_list.append(("miss", self.trial_time.elapsed()))

    def paintEvent(self, _) -> None:
        """Paint event.

        Draws the trail between the blazes.

        """
        t = self.current_trial
        if t:
            painter = QPainter(self)
            pen = QPen()
            pen.setWidth(4)
            painter.setPen(pen)
            rects = self.rects[: t.trial_number]
            for a, b in zip([None] + rects, rects + [None]):
                if a and b:
                    painter.drawLine(a.center(), b.center())

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Besides the basic summary stats, counts the total number of attempts and
        redefines accuracy as correct responses divided by attempts.

        Returns:
            dict: Summary statistics.

        """

        d = self.basic_summary()
        dic = {
            "total_duration_ms": d["total_duration_ms"],
            "total_duration_min": d["total_duration_min"],
        }
        blocks = set(t["block_type"] for t in self.procedure.completed_trials)
        for b in blocks:

            trials = [
                t for t in self.procedure.completed_trials if t["block_type"] == b
            ]
            trials = [t for t in trials if not t["practice"]]
            dic_ = self.basic_summary(adjust=True, trials=trials, prefix=b)
            logger.debug("changing what is meant by accuracy for this task")

            if dic_[b + "_completed_trials"] > 0:

                trials = [t for t in trials if "attempts" in t]
                attempts = sum(t["attempts"] for t in trials)
                dic_[b + "_attempts"] = attempts
                errors = sum(t["errors"] for t in trials)
                dic_[b + "_errors"] = errors
                denom = dic_[b + "_completed_trials"] + errors + attempts
                dic_[b + "_accuracy"] = dic_[b + "_completed_trials"] / denom

            else:

                dic_[b + "_accuracy"] = 0
                dic_[b + "_errors"] = 0
                dic_[b + "_accuracy"] = 0

            dic.update(dic_)
        return dic
