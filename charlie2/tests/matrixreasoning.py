"""
================
Matrix reasoning
================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/maxtrixreasoning.py

Description
===========

This is identical to the matrix reasoning test from the WAIS-III [1]_. On each trial,
the proband sees a matrix with one missing item in the centre of the screen, and an
array of alternatives below. The task is to select the correct element from the array by
clicking within its area. There is one practice trial, which will not progress until the
correct answer is selected. The test will terminate prematurely if four out of the last
five trials were incorrect. Probands can sometimes spend minutes on single trials of
this test. To try to prevent this, each trial has a time limit of 45 seconds. The
stimuli are taken direction from the WAIS-III.


Summary statistics
==================

* `completed` (bool): Did the proband complete the test?
* `responses` (int): Total number of responses.
* `any_skipped` (bool): Where any trials skipped?
* `time_taken` (int): Time taken to complete the entire test in ms.
* `correct` (int): How many trials correct?
* `accuracy` (float): proportion of correct responses.
* `resumed` (bool): Was this test resumed at some point?

Reference
=========

.. [1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
  Antonio, TX: The Psychological Corporation.

"""
__version__ = 2.0
__status__ = "production"

from logging import getLogger
from PyQt5.QtCore import QRect
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, all we need are the answers and path to the correct images."""
        answers = [
            1,
            3,
            1,
            3,
            2,
            0,
            0,
            2,
            4,
            4,
            4,
            1,
            2,
            0,
            1,
            3,
            2,
            0,
            0,
            3,
            4,
            4,
            1,
            1,
            0,
            4,
            3,
            2,
            2,
            3,
            0,
            3,
            1,
            2,
            4,
        ]
        return [
            {
                "trial_number": i,
                "answer": answer,
                "matrix": "M%03d.png" % (i + 1),
                "array": "M%03da.png" % (i + 1),
            }
            for i, answer in enumerate(answers)
        ]

    def block(self):
        """Set the trial time limit and display instructions."""
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """Show matrix and array, set up zones."""
        self.clear_screen(delete=True)
        matrix = self.display_image(self.data.current_trial.matrix, (0, 125))
        array = self.display_image(self.data.current_trial.array, (0, -125))

        # make zones
        rects = []
        for i in range(5):
            w = int(round(array.frameGeometry().width() / 5))
            h = array.frameGeometry().height()
            x = array.frameGeometry().x() + w * i
            y = array.frameGeometry().y()
            rects.append(QRect(x, y, w, h))
        self.make_zones(rects)

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1.

        """
        ix = [event.pos() in z for z in self.zones]
        t = self.data.current_trial
        if any(ix):
            t.rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = t.rsp == t.answer
            self.data.current_trial.status = "completed"

    def block_stopping_rule(self):
        """After five trials completed, exit if four or more were incorrect."""
        if len(self.data.completed_trials) > 5:
            trials = self.data.completed_trials[-5:]
            correct = len([t for t in trials if t["correct"]])
            logger.info("corect trials: %s/5" % str(correct))
            outcome = True if correct <= 1 else False
        else:
            outcome = False
        logger.info("should we stop? %s" % str(outcome))
        return outcome

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust_time_taken=True)
        return dic
