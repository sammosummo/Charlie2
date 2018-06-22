"""
=================
Trail-making test
=================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/trails.py

Description
===========

In this task, the proband must click on circles drawn on the screen in a specified
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
* `resumed` (bool): Was this test resumed at some point?

References
==========

.. [1] Reitan, R. M. (1958). Validity of the Trail Making test as an indicator of
  organic brain damage. Percept Mot Skills, 8, 271-276.

.. [2] Corrigan, J. D., & Hinkeldey, M. S. (1987). Relationships between parts A and B
  of the Trail Making Test. J Clin Psychol, 43(4), 402–409.

"""
__version__ = 2.0
__status__ = 'complete'


from PyQt5.QtGui import QPainter, QPen
from charlie2.tools.recipes import charlie2_trials
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each trial requires the block number (for indexing the on-
        screen instructions), the block type (practice blocks are not included in the
        summary), the trial number (to indicate when a new block starts), the target
        blaze position (where a correct click/press should go), and the glyph (to load
        the correct image). This was complicated to generate and required many manual
        edits, so was all done in a different script and simply imported here. """
        return charlie2_trials()

    def block(self):
        """For this test, display instructions, pre-load the images, pre-move them, set
        up zones, create a painter widget for drawing the trail."""
        dpct = self.data.proc.current_trial
        b = dpct.block_number
        
        # display instructions; do this first
        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # time limits depend on block type
        if dpct.block_type == "practice":
            self.block_max_time = 30
        else:
            self.block_max_time = 180

        # find all trials in this block
        trials = [dpct]  # bc first trial was popped
        trials += [t for t in self.data.proc.remaining_trials if t.block_number == b]

        # get their glyphs and positions
        glyphs = [t.glyph for t in trials]
        positions = [t.blaze_position for t in trials]

        # load the blazes but don't show them
        self.rects = []
        self.images = []
        for glyph, pos in zip(glyphs, positions):
            img = self.display_image(f"a_{glyph}.png", pos)
            self.images.append(img)
            img.hide()
            self.rects.append(img.frameGeometry())

        # make zones
        self.make_zones(self.rects)

    def trial(self):
        """For this test, just listen for a mouse click within the target blaze."""
        dpct = self.data.proc.current_trial
        
        # clear the screen but don't delete blazes
        self.clear_screen()

        # show the blazes
        [img.show() for img in self.images]

        # reset click/press counters
        dpct.misses = 0
        dpct.errors = 0

        # set target blaze
        self.target_blaze = self.rects[dpct.trial_number]

    def summarise(self):
        """See docstring for explanation."""
        names = {1: "num", 3: "let", 5: "numlet"}
        dic = {}

        for b, n in names.items():
            trials = [t for t in self.data.proc.completed_trials if t.block_number == b]
            dic_ = self.basic_summary(trials=trials, adjust_time_taken=True)
            dic_ = {n + '_' + k: v for k, v in dic_.items()}
            dic.update(dic_)

        return dic

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target blaze. If so,
        the trial is over. If not, register a miss or a non-target blaze."""
        dpct = self.data.proc.current_trial
        if event.pos() in self.target_blaze:
            dpct.completed = True
        elif any(event.pos() in z for z in self.zones):
            dpct.errors += 1
        else:
            dpct.misses += 1

    def paintEvent(self, _):
        """Need to override a Qt method to draw. Draw a trail (straight line) from the
        centre of one blaze to the centre of the other."""
        dpct = self.data.proc.current_trial
        if dpct:
            painter = QPainter(self)
            pen = QPen()
            pen.setWidth(4)
            painter.setPen(pen)
            rects = self.rects[: dpct.trial_number]
            for a, b in zip([None] + rects, rects + [None]):
                if a and b:
                    painter.drawLine(a.center(), b.center())
