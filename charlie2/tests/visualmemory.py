"""
=============
Visual memory
=============

:Version: 1.0
:Source: http://github.com/sammosummo/Charlie2/tests/visualmemory.py
:Author: Sam Mathias

Description
===========

This test is designed to measure the capacity of visual short-term memory for colours
using a change-localisation task similar to the one employed by [1]_. On each trial, the
proband sees 5 circles, each with a random colour. All circles are removed, then
reappear, but one has changed colour. The proband must click on/touch the changed
circle. There are 30 trials, but after 5 trials, the test will start evaluating
performance and will quit early if chance performance is detected. There is a 30-second
time limit on each trial and a 240-second time limit on the whole experiment.

Reference
=========

.. [1] Johnson, M. K., McMahon, R. P., Robinson, B. M., Harvey, A. N., Hahn, B.,
  Leonard, C. J., Luck, S. J., & Gold, J. M. (2013). The relationship between working
  memory capacity and broad measures of cognitive ability in healthy adults and people
  with schizophrenia. Neuropsychol, 27(2), 220-229.

"""
from sys import gettrace
from typing import List, Dict

from charlie2.tools.stats import basic_summary

__version__ = 1.0
__author__ = "Sam Mathias"

from logging import getLogger
from math import cos, pi, sin

from PyQt5.QtGui import QPixmap, QMouseEvent

from charlie2.tools.basetestwidget import BaseTestWidget

logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Set the block deadline to 300 s.
            3. Make a labels storage list.

        """
        super(TestWidget, self).__init__(parent)
        self.block_deadline = 300 * 1000
        self.labels = []

    def make_trials(self) -> List[Dict[str, float]]:
        """Generates new trials.

        Returns:
            :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `theta` (:obj:`float`)

        """
        names = ["trial_number", "theta"]
        thetas = [
            0.07287796,
            0.41152918,
            0.91638001,
            0.10786362,
            0.44804563,
            0.07869748,
            0.32707228,
            0.13110916,
            0.39891674,
            0.13511945,
            0.96472743,
            0.49840824,
            0.75278005,
            0.36421804,
            0.90371158,
            0.15003588,
            0.82969852,
            0.04375173,
            0.8420186,
            0.49465768,
            0.73329339,
            0.27312348,
            0.66541802,
            0.62325591,
            0.39011348,
            0.07071519,
            0.22071366,
            0.64990979,
            0.21862013,
            0.22426774,
        ]
        return [dict(zip(names, params)) for params in enumerate(thetas)]

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays task instructions with a key press to continue.

        """
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Hides the mouse and disables responses.
            2. Clears the screen.
            3. Displays the study array.
            4. Hide the study array
            5. Show the response array.
            6. Set up "zones".

        """

        t = self.current_trial

        logger.debug("commencing study phase of trial")
        self.mouse_visible = False
        self.performing_trial = False
        self.clear_screen(delete=False)

        logger.debug("about to display items")
        self.labels = []
        delta = 2 * pi / 4
        for item in range(4):
            theta = t.theta * 2 * pi + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            s = "l%i_t%i_i%i.png" % (4, t.trial_number, item)
            label = self.display_image(s, (x, y))
            self.labels.append(label)
        if gettrace() is None:  # checks whether running through a debugger
            self.sleep(3000)

        [label.hide() for label in self.labels]
        if gettrace() is None:
            self.sleep(2000)

        s = "l%i_t%i_i%i_r.png" % (4, t.trial_number, 0)
        self.labels[0].setPixmap(QPixmap(self.vis_stim_paths[s]))
        [label.show() for label in self.labels]

        self.make_zones([l.frameGeometry() for l in self.labels])
        self.mouse_visible = True
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
            t.correct = t.rsp == 0
            self.current_trial.status = "completed"

    def block_stopping_rule(self) -> bool:
        """Block stopping rule.

        Stop if below chance performance after 4 trials completed.

        Returns:
            bool: Should we stop?

        """
        trials = self.procedure.completed_trials
        logger.debug(str(trials))
        if len(trials) > 4:
            correct = [t for t in trials if t["correct"]]
            logger.debug(str(correct))
            logger.debug(str(len(correct) / len(trials)))
            return True if len(correct) / len(trials) <= .25 else False
        else:
            return False

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Additionally calculates K.

        Returns:
            dict: Summary statistics.

        """
        dic = basic_summary(self.procedure.completed_trials)
        dic["k"] = dic["accuracy"] * 4
        return dic
