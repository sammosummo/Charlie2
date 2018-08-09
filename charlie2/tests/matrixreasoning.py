"""
================
Matrix reasoning
================

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/maxtrixreasoning.py
:Author: Sam Mathias

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

Reference
=========

.. [1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
  Antonio, TX: The Psychological Corporation.

"""
from logging import getLogger
from sys import gettrace
from typing import Dict, List

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QMouseEvent

from charlie2.tools.basetestwidget import BaseTestWidget
from charlie2.tools.stats import basic_summary

__version__ = 2.0
__author__ = "Sam Mathias"


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        Returns:
            :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `answer` (:obj:`int`)
                3. `matrix` (:obj:`str`)
                4. `array` (:obj:`str`)

        """
        answers = [int(i) for i in "13132002444120132003441104322303124"]
        return [
            {
                "trial_number": i,
                "answer": answer,
                "matrix": "M%03d.png" % (i + 1),
                "array": "M%03da.png" % (i + 1),
            }
            for i, answer in enumerate(answers)
        ]

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays task instructions with a key press to continue.

        """
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen.
            2. Displays the matrix.
            3. Displays the array.
            4. Makes "zones" encapsulating array items.
            5. Sleeps for 1 s to prevent super-quick responses.

        """
        self.clear_screen(delete=True)
        self.display_image(self.current_trial.matrix, (0, 125))
        array = self.display_image(self.current_trial.array, (0, -125))

        # make zones
        rects = []
        for i in range(5):
            w = int(round(array.frameGeometry().width() / 5))
            h = array.frameGeometry().height()
            x = array.frameGeometry().x() + w * i
            y = array.frameGeometry().y()
            rects.append(QRect(x, y, w, h))
        self.make_zones(rects)

        # prevent super-quick responses
        if self.debugging is False:
            self.performing_trial = False
            self.sleep(1000)
            self.performing_trial = True

    def mousePressEvent_(self, event: QMouseEvent) -> None:
        """Mouse or touchscreen press event.

        If the event was within a zone, marks trial as complete and moves on.

        Args:
            event (PyQt5.QtGui.QMouseEvent)

        """
        ix = [event.pos() in z for z in self.zones]
        t = self.current_trial
        if any(ix):
            t.rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = t.rsp == t.answer
            self.current_trial.status = "completed"

    def block_stopping_rule(self) -> bool:
        """Block stopping rule.

        Stop the test if fewer than 1 trial correct out of the last five trials.

        Returns:
            bool: Should we stop?

        """
        logger.debug(f"completed trials: {self.procedure.completed_trials}")
        n = len(self.procedure.completed_trials)
        logger.debug(f"{n} trials completed")
        if n >= 5:
            trials = self.procedure.completed_trials[-5:]
            correct = len([t for t in trials if t["correct"]])
            logger.debug("correct trials: %s/5" % str(correct))
            outcome = True if correct <= 1 else False
        else:
            outcome = False
        logger.debug("should we stop? %s" % str(outcome))
        return outcome

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Redefines accuracy as the number correct divided by 35.

        Returns:
            dict: Summary statistics.

        """
        dic = basic_summary(self.procedure.completed_trials)
        dic["accuracy"] = dic["correct_trials"] / 35
        return dic
