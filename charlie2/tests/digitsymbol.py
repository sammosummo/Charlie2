"""
============
Digit symbol
============

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/digitsymbol.py
:Author: Sam Mathias

Description
===========

This test was originally designed by D. Glahn for an earlier computerised test battery
called STAN [1]_. Although it shares its name with a pen-and-paper test found in the
WAIS-III [2]_, it is not known how performance on the two tests is related.

On each trial, the proband sees a key of digits and symbols at the top of the screen, as
well as a single digit and a single symbol in the centre of the screen. The proband
indicates whether the target symbol matches the target digit according to the key by
responding either 'yes' or 'no'. During a test block, the proband completes as many
trials as they can within 90 seconds. The symbols currently the same as those in the
STAN.

This test is modified from Charlie version 1 [3]_ to include a second 90-s test block.
The two blocks are identical in design.

References
==========

.. [1] Glahn, D. C., Almasy, L., Blangero, J., Burk, G. M., Estrada, J., Peralta, J. M.,
  Meyenberg, N., Castro, M. P., Barrett, J., Nicolini, H., Raventós, H., & Escamilla, M.
  A. (2007). Adjudicating neurocognitive endophenotypes for schizophrenia. Am. J. Med.
  Genet. B. Neuropsychiatr. Genet., 44B(2), 242-249.

.. [2] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
  Antonio, TX: The Psychological Corporation.

.. [3] Mathias, S. R., Knowles, E. E. M., Barrett, J., Leach, O., Buccheri S., Beetham,
  T., Blangero, J., Poldrack, R.A., & Glahn, D. C. (2017). The processing- speed
  impairment in psychosis is more than just accelerated aging. Schizophr. Bull., 43(4),
  814–823.

"""
from sys import gettrace

from charlie2.tools.stats import basic_summary

__version__ = 2.0
__author__ = "Sam Mathias"


from logging import getLogger
from typing import Dict, List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from ..tools.basetestwidget import BaseTestWidget
from ..tools.recipes import digits, symbols

logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Sets a block deadline of 90s (for practice, too).
            3. Hide the mouse.
            4. Define x-positions of digits and symbols in the key.
            5. Load and hide the key.

        """
        super(TestWidget, self).__init__(parent)
        if gettrace() is None:
            self.block_deadline = 90 * 1000
        else:
            self.block_deadline = 4 * 1000
        self.mouse_visible = False
        self.symbols = [self.load_image(f"sym{i}.png") for i in range(1, 10)]
        self.digits = [self.load_text(str(i)) for i in range(1, 10)]
        self.xs = range(-300, 350, 75)
        self.digit = None
        self.symbol = None

    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

            Returns:
                :obj:`list`: Each entry is a dict containing:
                    1. `trial_number` (:obj:`int`)
                    2. `block_number` (:obj:`int`)
                    3. `practice` (:obj:`bool`)
                    4: `digit` (:obj:`int`)
                    5. `symbol` (:obj:`int`)

        """

        blocks = ([0] * 5) + ([1] * 295) + ([2] * 300)
        practices = ([True] * 5) + ([False] * 595)
        trials = list(range(5)) + list(range(295)) + list(range(300))
        names = ["block_number", "practice", "trial_number", "digit", "symbol"]
        details = zip(blocks, practices, trials, digits, symbols)

        return [dict(zip(names, t)) for t in details]

    def block(self) -> None:
        """New block.

        Does the following:
            1. Pre-load digits and symbols.
            2. Displays block-specific task instructions with a key press to continue.

        """
        for symbol, digit, x in zip(self.symbols, self.digits, self.xs):
            g = self.move_widget(symbol, (x, 250))
            symbol.hide()
            digit.resize(g.size())
            self.move_widget(digit, (x, 200))
            digit.hide()
        b = self.current_trial.block_number
        self.display_instructions_with_space_bar(self.instructions[4 + b])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen (but doesn't delete).
            2. Displays the arrow keys and their labels.
            3. Displays the key.
            4. Shows the target digt and symbol.

        """
        self.clear_screen(delete=False)
        self.display_keyboard_arrow_keys(self.instructions[2:4])
        [l.show() for l in self.symbols + self.digits]
        s = self.current_trial.symbol
        d = self.current_trial.digit
        self.symbol = self.display_image(f"sym{s}.png", (0, 25))
        self.digit = self.display_text(str(d), (0, -25))

    def keyReleaseEvent_(self, event: QKeyEvent) -> None:
        """Key release event.

        If the event was a release of either the left or right arrow keys, records a
        response. Displays feedback (if a practice trial) and moves onto the next trial.

        Args:
            event (PyQt5.QtGui.QKeyEvent)

        """
        dic = {Qt.Key_Left: True, Qt.Key_Right: False}
        t = self.current_trial

        if event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == (t.symbol == t.digit)
            t.status = "completed"
            self.symbol.deleteLater()
            self.digit.deleteLater()
            if t.practice:
                s = self.instructions[7:9][not t.correct]
                a = self.display_text(s, (0, -100))
                self.sleep(1000)
                a.hide()
                a.deleteLater()

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Besides the basic summary stats, calculates an adjusted score as the number of
        correct trials divided by accuracy. Creates summaries for each block separately
        and all trials together.

        Returns:
            dict: Summary statistics.

        """
        trials = self.procedure.completed_trials
        dic = basic_summary(trials)
        dic["adjusted_score"] = dic["correct_trials"] * dic["accuracy"]
        for b in [1, 2]:
            trials_ = [t for t in trials if t["block_number"] == b]
            dic.update(basic_summary(trials_, prefix=str(b)))
        return dic
