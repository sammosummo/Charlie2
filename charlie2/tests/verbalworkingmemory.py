"""
=====================
Verbal working memory
=====================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/verbalworkingmemory.py

Description
===========

This test is a combination of the digit span forward, digit span backward, and letter-
number sequencing tests from the WAIS-III and WMC-III [1]_. This test requires the
proband to relinquish control to the experimenter. There are four blocks in the test.
In the first block, the experimenter reads aloud sequences of letters and digits to the
proband. The proband then repeats the sequence back to the experimenter, in the same
order. The first sequence is two digits in length; sequence length increases by one
digit every two sequences. If the proband responds incorrectly to both sequences of the
same length, the block is terminated. The second block is the same as the first except
that probands repeat the sequences in reverse order. In the third phase, the sequences
contain both digits and letters, and probands repeat the letters in numerical order,
followed by the letters in alphabetical order. The third block serves as a practice for
the fourth block. In the fourth block there are three sequences of the same length; if
probands get all three wrong, the block is terminated.


Summary statistics
==================

For `{x}` in [`forward`, `backward`, `lns`]:

* `{x}_completed` (bool): Did the proband complete the test?
* `{x}_correct` (int): Number of correct responses.
* `{x}_responses` (int): Total number of responses in the block.
* `{x}_k` (int): Length of the longest sequence reported.
* `resumed` (bool): Was this test resumed at some point?


Reference
=========

.. [1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
  Antonio, TX: The Psychological Corporation.

"""
__version__ = 2.0
__status__ = 'production'


from logging import getLogger
from PyQt5 import QtCore, QtWidgets
from charlie2.tools.testwidget import BaseTestWidget
from charlie2.tools.recipes import get_vwm_stimuli


logging = getLogger(__name__)


class TestWidget(BaseTestWidget):

    def make_trials(self):
        """For this test, block_type indicates whether this is the forward, backward,
        lns_prac, or lns blocks."""
        sequences = get_vwm_stimuli(self.args.language)
        trial_types = ['forward', 'backward', 'lns_prac', 'lns']
        practices = {'forward': , 'backward', 'lns_prac', 'lns']}
        details = []
        for block, sequences_ in enumerate(sequences):
            for trial, sequence in enumerate(sequences_):
                details.append({
                    'block_number': block,
                    'trial_number': trial,
                    'block_type': trial_types[block],
                    'sequence': str(sequence),
                    'length': len(str(sequence)),
                })
        return details

    def block(self):
        """Fro this test, display instructions fro experimenter to read out to proband.
        If this is the very first trial, additionally display instructions to the
        proband."""
        dpct = self.data.proc.current_trial
        self.skip_countdown = True
        s = self.instructions[5 + dpct.block_number]
        label, btn = self.display_instructions_with_continue_button(s)

        # if very first trial, show message to proband
        if dpct.first_trial_in_test:
            label.hide()
            btn.hide()
            s = self.instructions[4]
            a, b = self.display_instructions_with_continue_button(s)
            b.clicked.disconnect()
            b.clicked.connect(lambda: [a.hide(), b.hide(), btn.show(), label.show()])

    def trial(self):
        """For this test, display the GUI."""
        dpct = self.data.proc.current_trial

        # calculate the corect answer
        if dpct.block_type == 'forward':
            answer = dpct.sequence
        elif dpct.block_type == 'backward':
            answer = dpct.sequence[::-1]
        else:
            digits = []
            letters = []
            for a in dpct.sequence:
                if a.isdigit():
                    digits.append(a)
                elif a.isalpha():
                    letters.append(a)
            answer = sorted(digits) + sorted(letters)

        # instructions and buttons
        self.display_instructions(self.instructions[9] % '-'.join(dpct.sequence))
        corr_button = self._display_continue_button()
        corr_button.setText(self.instructions[10] % '-'.join(answer))
        corr_button.resize(corr_button.sizeHint())
        x = (self.frameGeometry().width() - corr_button.width()) // 2 - 175
        y = self.frameGeometry().height() - (corr_button.height() + 20)
        corr_button.move(x, y)
        corr_button.clicked.disconnect()
        corr_button.clicked.connect(self._correct)
        incorr_button = self._display_continue_button()
        incorr_button.setText(self.instructions[11])
        incorr_button.resize(incorr_button.sizeHint())
        x = (self.frameGeometry().width() - incorr_button.width()) // 2 + 175
        y = self.frameGeometry().height() - (incorr_button.height() + 20)
        incorr_button.move(x, y)
        incorr_button.clicked.disconnect()
        incorr_button.clicked.connect(self._incorrect)

    def _correct(self):
        dpct = self.data.proc.current_trial
        if dpct:
            dpct.correct = True
            dpct.completed = True
            dpct.rt = self.trial_time.elapsed()
            dpct.time_elapsed = self.block_time.elapsed()
            self.next_trial()

    def _incorrect(self):
        dpct = self.data.proc.current_trial
        if dpct:
            dpct.correct = False
            dpct.completed = True
            dpct.rt = self.trial_time.elapsed()
            dpct.time_elapsed = self.block_time.elapsed()
            self.next_trial()

    def summarise(self):
        """See docstring for explanation."""
        blocks = ['forward', 'backward', 'lns']
        dic = {}
        cts = self.data.proc.completed_trials
        for b in blocks:
            trials = [t for t in cts if t.block_type == b and t.completed is True]
            for trial in trials: print(vars(trial))
            dic_ = self.basic_summary(trials=trials, adjust_time_taken=False)
            # dic_['responses'] += 1  # This task undercounts responses by 1.
            if 'accuracy' in dic_: del dic_['accuracy']  # not meaningful
            if 'time_taken' in dic_: del dic_['time_taken']  # not meaningful
            trial = [t for t in trials if t.correct][-1]
            dic_['k'] = trial.length
            dic.update({f"{b}_{k}": v for k, v in dic_.items()})
        return dic

    def mousePressEvent(self, event):
        """We don't want to handle mouse presses in the same way as other tests."""
        pass

    def stopping_rule(self):
        """Checks to see if the proband got both or all three (depending on the
        phase) sequences of the same length incorrect. If True, all sequences
        of this phase remaining in the control iterable are removed."""
        dpct = self.data.proc.current_trial
        if dpct.correct or dpct.block_type == 'lns_prac':
            return False
        else:
            ct = self.data.proc.completed_trials
            trials = [t for t in ct if t.block_number == dpct.block_number]
            trials = [t for t in trials if t.length == dpct.length]
            if 'lns' in dpct.block_type:
                n = 2
            else:
                n = 1
            if len(trials) == n and all(not t.correct for t in trials):
                return True
            else:
                return False
