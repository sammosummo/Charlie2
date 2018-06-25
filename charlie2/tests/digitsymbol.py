"""
====================
Digit symbol test
====================

:Status: complete
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
__status__ = 'complete'


from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, trials require the trial_number, block number, block type,
        digit and symbol. There is an arbitrarily large number of trials (600). The task
        will almost certainly time out before all trials are completed."""
        blocks = ([0] * 5) + ([1] * 295) + ([2] * 300)
        block_type = (["practice"] * 5) + (["test"] * 595)
        trials = list(range(5)) + list(range(295)) + list(range(300))
        digits = [
            7,1,5,9,2,4,1,6,6,7,7,9,1,8,8,8,1,7,2,2,5,1,1,9,5,2,7,9,3,1,7,1,2,2,1,1,2,2,
            1,8,1,1,3,3,7,2,4,5,5,9,8,6,1,8,6,8,3,1,5,8,8,7,2,5,1,1,2,1,4,6,9,7,7,5,8,8,
            6,8,1,2,5,7,4,5,3,3,9,2,4,9,7,5,6,4,4,1,1,8,2,2,5,9,8,6,8,2,9,4,8,4,3,1,1,8,
            8,1,6,1,6,4,4,4,7,3,2,8,8,8,2,4,4,5,8,8,2,5,3,1,1,1,8,7,3,4,4,3,5,4,2,4,6,1,
            3,3,1,7,6,7,9,3,8,7,5,4,5,5,6,9,5,2,9,1,8,3,1,1,1,5,5,8,1,8,9,2,1,7,6,1,7,9,
            4,2,5,6,2,5,2,7,3,7,9,4,3,1,3,6,1,5,2,4,8,5,1,5,7,4,4,9,6,3,6,3,9,1,9,2,1,5,
            2,1,4,6,9,6,5,7,2,5,8,5,9,2,4,7,8,3,9,1,9,1,7,2,8,7,4,1,3,2,1,6,4,7,6,1,7,5,
            4,4,2,3,6,8,3,4,9,9,3,7,3,6,6,6,5,5,1,2,9,7,1,1,9,5,3,3,8,6,5,8,5,6,5,6,1,6,
            1,8,5,5,5,8,5,9,1,9,9,6,1,6,9,4,8,1,2,5,1,5,8,6,3,6,1,8,4,2,9,9,4,3,2,1,8,7,
            8,5,2,7,3,2,9,4,9,3,7,7,7,5,9,7,3,5,5,2,4,6,9,6,3,2,4,4,7,8,9,4,2,1,5,1,8,7,
            5,8,6,8,7,1,4,7,7,3,7,3,1,2,5,4,1,4,8,3,6,7,3,6,9,2,9,9,1,3,1,7,3,6,6,1,5,1,
            5,7,4,8,4,7,8,5,6,3,3,2,9,9,4,5,5,8,2,8,2,2,2,8,5,1,1,9,6,6,6,3,2,3,1,5,8,4,
            8,5,7,7,8,7,1,3,4,3,5,9,6,3,7,6,7,5,3,5,4,2,9,5,2,5,1,7,7,4,1,4,1,2,1,2,8,1,
            3,6,3,8,4,7,6,9,3,2,2,5,8,2,6,9,3,4,7,7,6,6,2,9,3,7,8,8,8,6,8,2,4,1,5,1,9,8,
            9,3,9,2,3,6,4,8,9,5,3,7,7,1,7,5,6,7,5,1,4,8,4,4,8,2,6,2,8,9,1,3,7,9,2,4,1,3,
            6,9,7,3,2,3,2,2,8,8,8,4,6,3,1,4,2,5,9,8,6,1,9,4,7,1,4,8,1,2]
        symbols = [
            2,1,5,6,7,4,1,9,6,6,7,9,7,5,8,7,1,5,9,7,9,6,1,9,5,2,7,9,3,1,5,1,4,2,1,1,5,9,
            3,7,1,7,3,1,7,2,4,5,5,3,9,6,1,8,9,4,1,1,5,8,8,7,1,7,7,8,2,1,4,8,9,7,7,6,8,8,
            6,8,3,9,5,7,8,6,3,8,9,2,4,9,6,6,6,6,4,9,1,5,2,2,7,2,8,6,8,2,4,3,8,4,3,1,1,1,
            4,1,1,1,9,7,6,7,7,3,2,8,8,8,7,4,4,5,4,3,2,8,1,8,1,1,3,6,3,9,4,3,9,4,2,4,6,1,
            2,3,1,7,1,1,8,3,6,1,1,2,5,8,6,9,5,6,9,6,7,2,1,7,1,5,3,8,1,1,3,4,1,2,6,1,9,9,
            8,2,5,4,9,5,2,1,3,3,4,7,9,1,3,5,1,5,2,2,8,2,1,2,1,7,2,9,4,3,9,2,8,1,2,2,1,4,
            7,7,2,9,9,1,4,7,6,5,7,5,6,2,4,2,8,3,9,1,9,5,7,5,8,8,2,1,3,3,4,6,4,4,6,1,7,7,
            7,4,1,3,6,8,3,4,4,9,2,3,3,4,6,8,5,5,1,5,5,3,1,1,9,9,8,3,8,6,3,8,5,6,5,6,1,6,
            1,8,5,5,9,8,1,9,1,2,1,6,1,4,7,4,8,2,2,9,1,3,8,6,1,6,1,8,4,3,9,9,4,3,9,2,8,2,
            7,5,9,7,1,2,1,4,1,3,1,7,9,1,3,7,3,5,5,8,5,7,4,6,5,9,4,4,7,8,7,3,2,4,5,1,9,7,
            5,1,6,8,8,4,4,7,7,1,7,1,4,4,5,4,4,4,8,3,2,7,8,6,6,2,5,9,8,3,1,7,3,8,7,1,5,8,
            5,3,7,6,4,7,8,5,9,9,3,1,5,9,4,7,5,8,9,8,2,2,2,8,3,1,1,2,3,6,6,3,2,7,1,4,8,4,
            8,6,7,7,7,2,1,8,4,2,5,4,6,8,7,6,7,5,1,3,1,2,7,2,2,6,1,9,7,5,1,6,8,3,1,1,5,4,
            3,6,3,2,6,8,6,9,3,7,3,5,8,1,4,8,3,3,9,7,6,6,2,4,3,2,8,8,7,6,3,2,4,1,7,6,4,8,
            2,3,7,2,1,6,4,9,2,8,2,7,1,5,2,5,6,7,5,1,8,8,8,4,8,2,1,2,8,9,1,1,7,8,2,4,4,3,
            6,4,7,1,2,3,7,8,4,8,8,4,6,5,1,6,2,5,9,8,7,3,1,7,2,8,4,8,3,1]
        names = ["block_number", "block_type", "trial_number", "digit", "symbol"]
        details = zip(blocks, block_type, trials, digits, symbols)
        return [dict(zip(names, t)) for t in details]

    def block(self):
        """For this test, display instructions and pre-load the images."""
        dpct = self.data.proc.current_trial
        b = dpct.block_number
        if dpct.block_type == "practice":
            self.block_max_time = 20
        else:
            self.block_max_time = 90
        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # load and move key symbols and digits
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

    def trial(self):
        """Fairly simple for this test."""
        dpct = self.data.proc.current_trial
        self.mouse_on = False
        self.clear_screen()

        # draw key and keyboard keys
        [l.show() for l in self.symbols + self.digits + self.keyboard_keys]

        # select and draw the target symbol and digit
        self.symbol = self.display_image(f"sym%i.png" % dpct.symbol, (0, 25))
        self.digit = self.display_text(str(dpct.digit), (0, -25))

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust_time_taken=False)
        del dic['any_skipped']  # obviously true for this test
        dic['adjusted_score'] = dic['responses'] * dic['accuracy']
        return dic

    def keyReleaseEvent_(self, event):
        """For this trial, listen for left- and right-arrow keyboard key
        presses."""
        dpct = self.data.proc.current_trial
        dic = {Qt.Key_Left: True, Qt.Key_Right: False}

        if event.key() in dic:

            dpct.rsp = dic[event.key()]
            dpct.correct = dpct.rsp == (dpct.symbol == dpct.digit)
            dpct.completed = True

            # should prevent dozens of old labels being stored in memory
            self.symbol.deleteLater()
            self.digit.deleteLater()

            # feedback?
            if dpct.block_type == "practice":
                s = self.instructions[7:9][not dpct.correct]
                a = self.display_text(s, (0, -100))
                self.sleep(1)
                a.hide()
                a.deleteLater()
