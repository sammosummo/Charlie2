"""
=============
Visual memory
=============

:Status: complete
:Version: 1.0
:Source: http://github.com/sammosummo/Charlie2/tests/visualmemory.py

Description
===========

This test is designed to measure the capacity of visual short-term memory for colours
using a change-localisation task similar to the one employed by [1]_. On each trial, the
proband sees 5 circles, each with a random colour. All circles are removed, then
reappear, but one has changed colour. The proband must click on/touch the changed
circle. There are 30 trials, but after 5 trials, the test will start evaluating
performance and will quit early if chance performance is detected. There is a 30-second
time limit on each trial and a 240-second time limit on the whole experiment.


Summary statistics
==================

* `completed` (bool): Did the proband complete the test?
* `responses` (int): Total number of responses.
* `any_skipped` (bool): Where any trials skipped?
* `time_taken` (int): Time taken to complete the entire test in ms.
* `correct` (int): How many trials correct?
* `resumed` (bool): Was this test resumed at some point?
* `accuracy` (float): proportion of correct responses.
* `k` (float): Accuracy multiplied by 5.

Reference
=========

.. [1] Johnson, M. K., McMahon, R. P., Robinson, B. M., Harvey, A. N., Hahn, B.,
  Leonard, C. J., Luck, S. J., & Gold, J. M. (2013). The relationship between working
  memory capacity and broad measures of cognitive ability in healthy adults and people
  with schizophrenia. Neuropsychol, 27(2), 220-229.

"""
__version__ = 1.0
__status__ = "production"

from logging import getLogger
from math import cos, sin, pi
from PyQt5.QtGui import QPixmap
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        names = ["trial_number", "theta"]
        thetas = [
            0.28335521,
            0.68132415,
            0.18400396,
            0.66522286,
            0.77395755,
            0.17858136,
            0.856814,
            0.1634176,
            0.57683277,
            0.24352501,
            0.26439799,
            0.42721477,
            0.0490913,
            0.11709211,
            0.61611725,
            0.11733051,
            0.13074312,
            0.34707225,
            0.13944024,
            0.83049628,
            0.18730887,
            0.16631436,
            0.26145498,
            0.28501413,
            0.93550665,
            0.5007598,
            0.52836678,
            0.42675553,
            0.49499377,
            0.78333836,
        ]
        return [dict(zip(names, params)) for params in enumerate(thetas)]

    def block(self):
        """If this is the first block, simply display instructions."""
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this trial, show the study and test arrays, and record responses."""
        t = self.data.current_trial

        logger.info("commencing study phase of trial")
        self.mouse_visible = False
        self.performing_trial = False
        self.clear_screen(delete=False)
        self.display_text(self.instructions[5], (0, -225))
        # if not t.first_trial_in_block:
        #     self.sleep(1)  # makes it less confusing when the new trial starts

        logger.info("about to display items")
        self.labels = []
        delta = 2 * pi / 5
        for item in range(5):
            theta = t.theta * 2 * pi + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            s = "l%i_t%i_i%i.png" % (5, t.trial_number, item)
            label = self.display_image(s, (x, y + 75))
            self.labels.append(label)
        self.sleep(3000)

        [label.hide() for label in self.labels]
        self.sleep(2000)

        s = "l%i_t%i_i%i_r.png" % (5, t.trial_number, 0)
        self.labels[0].setPixmap(QPixmap(self.vis_stim_paths[s]))
        [label.show() for label in self.labels]

        self.make_zones(l.frameGeometry() for l in self.labels)
        self.mouse_visible = True
        self.performing_trial = True

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1.

        """
        ix = [event.pos() in z for z in self.zones]
        t = self.data.current_trial
        if any(ix):
            t.rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = t.rsp == 0
            self.data.current_trial.status = "completed"

    def block_stopping_rule(self):
        """After five trials completed, exit if at chance."""
        trials = self.data.completed_trials
        logger.debug(str(trials))
        if len(trials) > 5:
            correct = [t for t in trials if t["correct"]]
            logger.debug(str(correct))
            logger.debug(str(len(correct) / len(trials)))
            return True if len(correct) / len(trials) <= .2 else False
        else:
            return False

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust_time_taken=True)
        return dic
