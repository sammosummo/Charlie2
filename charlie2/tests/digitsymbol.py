"""
============
Digit symbol
============

:Status: production
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/digitsymbol.py

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
The blocks are identical in design.

Summary statistics
==================

* `completed` (bool): Did the proband complete the test?
* `responses` (int): Total number of responses.
* `correct` (int): How many trials correct?
* `resumed` (bool): Was this test resumed at some point?
* `accuracy` (float): proportion of correct responses.
* `adjusted_score` (float): number of correct responses multiplied by accuracy.

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
__version__ = 2.0
__status__ = "production"


from logging import getLogger
from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget
from charlie2.recipes.digitsymbol import digits, symbols


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, trials require the trial_number, block number, digit and
        symbol. There is an arbitrarily large number of trials (600). The task
        will almost certainly time out before all trials are completed. To make this
        script easier to read, pre-generated digit and symbol orders are imported from
        `recipes`.

        """
        blocks = ([0] * 5) + ([1] * 295) + ([2] * 300)
        practices = ([True] * 5) + ([False] * 595)
        trials = list(range(5)) + list(range(295)) + list(range(300))
        names = ["block_number", "practice", "trial_number", "digit", "symbol"]
        details = zip(blocks, practices, trials, digits, symbols)
        return [dict(zip(names, t)) for t in details]

    def block(self):
        """For this test, display instructions and pre-load the images."""
        if self.data.current_trial.block_number > 0:
            logger.info("adding block deadline")
            self.block_deadline = 90 * 1000
        else:
            logger.info("block deadline set to None")
            self.block_deadline = None
        b = self.data.current_trial.block_number
        self.display_instructions_with_space_bar(self.instructions[4 + b])
        self.symbols = [self.load_image(f"sym{i}.png") for i in range(1, 10)]
        self.digits = [self.load_text(str(i)) for i in range(1, 10)]
        self.xs = range(-300, 350, 75)
        for symbol, digit, x in zip(self.symbols, self.digits, self.xs):
            g = self.move_widget(symbol, (x, 250))
            symbol.hide()
            digit.resize(g.size())
            self.move_widget(digit, (x, 200))
            digit.hide()
        self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[2:4])

    def keyReleaseEvent_(self, event):
        """For this trial, listen for left- and right-arrow keyboard key
        presses."""
        dic = {Qt.Key_Left: True, Qt.Key_Right: False}
        t = self.data.current_trial
        if event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == (t.symbol == t.digit)
            t.status = "completed"

            # should prevent dozens of old labels being stored in memory
            self.symbol.deleteLater()
            self.digit.deleteLater()

            # feedback?
            if t.practice:
                s = self.instructions[7:9][not t.correct]
                a = self.display_text(s, (0, -100))
                self.sleep(1000)
                a.hide()
                a.deleteLater()

    def trial(self):
        """Fairly simple for this test."""
        self.clear_screen(delete=False)
        [l.show() for l in self.symbols + self.digits + self.keyboard_keys]
        s = self.data.current_trial.symbol
        d = self.data.current_trial.digit
        self.symbol = self.display_image(f"sym{s}.png", (0, 25))
        self.digit = self.display_text(str(d), (0, -25))

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust_time_taken=True)
        return dic
