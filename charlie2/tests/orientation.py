"""
===========
Orientation
===========

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/orientation.py
:Author: Sam Mathias

Description
===========

This simple test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to press the
square as quickly as possible. It is similar to the mouse practice task from [1]_. There
are 20 trials in total and the test automatically times out after 60 s.

Unlike version 1, this version does not include lures.

Reference
=========

.. [1] Gur, R. C., Ragland, D., Moberg, P. J., Turner, T. H., Bilker, W. B., Kohler, C.,
  Siegel, S. J., & Gur, R. E. (2001). Computerized neurocognitive scanning: I.
  Methodology and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""
from sys import gettrace

__version__ = 2.0
__author__ = "Sam Mathias"


from logging import getLogger
from typing import Dict, List

from PyQt5.QtGui import QMouseEvent

from charlie2.tools.basetestwidget import BaseTestWidget
from charlie2.tools.stats import basic_summary

logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Sets a block deadline of 60s.

        """
        super(TestWidget, self).__init__(parent)
        self.block_deadline = 60 * 1000

    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        Returns:
             :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `position` (:obj:`tuple` of :obj:`int`): Defines the centre of the red
                square in pixels with respect to the centre of the display.

        """
        pos = [
            (263, -23),
            (-190, 313),
            (337, -240),
            (399, -14),
            (314, 54),
            (-346, 186),
            (-104, 157),
            (-10, -110),
            (-273, 149),
            (-420, -197),
            (3, -184),
            (294, 1),
            (60, 298),
            (335, 73),
            (-7, -313),
            (-134, 296),
            (475, -241),
            (75, 278),
            (118, -139),
            (310, 173),
        ]
        trials = [{"trial_number": i, "position": p} for i, p in enumerate(pos)]
        if gettrace() is not None:
            logger.debug("running in debug mode, so just running 5 trials")
            trials = trials[:5]
        return trials

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays the task instructions with a continue button.

        This test contains just one block.

        """
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen.
            2. Resets the number of "attempts" (screen presses not in the red square).
            3. Resets a list for recording time and position of attempts.
            4. Displays the red square.
            5. Makes the area of the red square a "zone".

        """
        self.clear_screen(delete=True)
        self.current_trial.attempts = 0
        self.current_trial.responses = []
        square = self.display_image("0_s.png", self.current_trial.position)
        self.make_zones([square.frameGeometry()])

    def mousePressEvent_(self, event: QMouseEvent) -> None:
        """Mouse or touchscreen press event.

        If the event was within the zone, marks trial as complete and moves on.
        Otherwise, logs an attempt and stays on the current trial.

        Args:
            event (PyQt5.QtGui.QMouseEvent)

        """
        rsp = (self.trial_time.elapsed(), (event.x(), event.y()))
        self.current_trial.responses.append(rsp)
        if event.pos() in self.zones[0]:
            self.current_trial.correct = True
            self.current_trial.status = "completed"
        else:
            self.current_trial.attempts += 1

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Besides the basic summary stats, counts the total number of attempts and
        redefines accuracy as correct responses divided by attempts.

        Returns:
            dict: Summary statistics.

        """
        trials = self.procedure.completed_trials
        dic = basic_summary(trials, adjust=True)
        correct_trials = [t for t in trials if t["correct"] is True]
        if len(correct_trials) > 0:
            dic["total_attempts"] = sum(t["attempts"] for t in correct_trials)
            denom = len(trials) + dic["total_attempts"]
            dic["accuracy"] = len(correct_trials) / denom
        return dic
