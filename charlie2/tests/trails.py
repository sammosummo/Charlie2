"""
============
Trail making
============

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/make_trail_trials.py

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

Summary statistics
==================

For `{x}` in [`num`, `let`, `numlet`]:

* `{x}_completed` (bool): Did the proband complete the test?
* `{x}_responses` (int): Total number of responses.
* `{x}_any_skipped` (bool): Where any trials skipped?
* `{x}_time_taken` (int): Time taken to complete the entire test in ms.
* `{x}_blaze_errors` (int): Number of incorrect blazes pressed.
* `{x}_misses` (int): Number of presses to areas not inside any blaze.
* `resumed` (bool): Was this test resumed at some point?

References
==========

.. [1] Reitan, R. M. (1958). Validity of the Trail Making test as an indicator of
  organic brain damage. Percept Mot Skills, 8, 271-276.

.. [2] Corrigan, J. D., & Hinkeldey, M. S. (1987). Relationships between parts A and B
  of the Trail Making Test. J Clin Psychol, 43(4), 402–409.

"""
__version__ = 2.0


from logging import getLogger
from PyQt5.QtGui import QPainter, QPen
from charlie2.tools.testwidget import BaseTestWidget
from charlie2.recipes.trails import make_trail_trials


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each trial requires the block number (for indexing the on-
        screen instructions), the block type (practice blocks are not included in the
        summary), the trial number (to indicate when a new block starts), the target
        blaze position (where a correct click/press should go), and the glyph (to load
        the correct image). This was complicated to generate and required many manual
        edits, so was all done in a different script and simply imported here."""
        return make_trail_trials()

    def block(self):
        """For this test, display instructions, pre-load the images, set up zones, and
        create a painter widget for drawing the trail."""
        self.block_deadline = 120 * 1000
        b = self.data.current_trial.block_number


        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # find all trials in this block
        trials = [self.data.current_trial]  # because first trial was popped
        trials += [t for t in self.data.remaining_trials if t["block_number"] == b]

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

    def trial(self):
        """For this test, just listen for a mouse press within the target blaze."""
        self.clear_screen(delete=False)
        t = self.data.current_trial

        # show the blazes
        if not t.first_trial_in_block:
            [img.show() for img in self.images + [self.tick]]
        else:
            [img.show() for img in self.images]

        # reset click/press counters

        t.attempts = 0
        t.errors = 0
        t.responses_list = []

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1.

        """
        ix = [event.pos() in z for z in self.zones]
        t = self.data.current_trial
        if any(ix):
            logger.info("clicked within a blaze")
            rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = rsp == t.trial_number
            t.responses_list.append((rsp, self.trial_time.elapsed()))

            if t.correct:
                logger.info("clicked within the correct blaze")
                self.data.current_trial.status = "completed"
            else:
                logger.info("clicked within a different blaze")
                t.errors += 1
                t.attempts += 1
        else:
            logger.info("clicked outside a blaze")
            t.attempts += 1
            t.responses_list.append(("miss", self.trial_time.elapsed()))

    def paintEvent(self, _):
        """Need to override a Qt method to draw. Draw a trail (straight line) from the
        centre of one blaze to the centre of the other."""
        t = self.data.current_trial
        if t:
            painter = QPainter(self)
            pen = QPen()
            pen.setWidth(4)
            painter.setPen(pen)
            rects = self.rects[: t.trial_number]
            for a, b in zip([None] + rects, rects + [None]):
                if a and b:
                    painter.drawLine(a.center(), b.center())

    def summarise(self):
        """See docstring for explanation."""
        dic = {}
        blocks = set(t["block_type"] for t in self.data.completed_trials)
        for b in blocks:
            trials = [t for t in self.data.completed_trials if t["block_type"] == b]
            dic_ = self.basic_summary(adjust=True, trials=trials, prefix=b)
            logger.info("changing what is meant by accuracy for this task")
            if dic_[b + "_completed_trials"] > 0:
                trials = [t for t in self.data.completed_trials if "attempts" in t]
                errors = sum(t["errors"] for t in trials)
                denom = dic_[b + "_completed_trials"] + errors
                dic_[b + "_accuracy"] = dic_[b + "_completed_trials"] / denom
            else:
                dic_[b + "accuracy"] = 0
            dic.update(dic_)
        return dic
