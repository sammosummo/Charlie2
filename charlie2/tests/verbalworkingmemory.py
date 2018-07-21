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
__status__ = "production"


from logging import getLogger
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QSound
from charlie2.tools.testwidget import BaseTestWidget
from charlie2.recipes.verbalworkingmemory import get_vwm_stimuli


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, block_type indicates whether this is the forward, backward,
        lns_prac, or lns blocks.

        """
        sequences = get_vwm_stimuli(self.kwds["language"])
        trial_types = ["forward", "backward", "lns_prac", "lns"]
        practices = {
            "forward": False,
            "backward": False,
            "lns_prac": True,
            "lns": False,
        }
        details = []
        for block, sequences_ in enumerate(sequences):
            for trial, sequence in enumerate(sequences_):
                details.append(
                    {
                        "block_number": block,
                        "trial_number": trial,
                        "block_type": trial_types[block],
                        "practice": practices[trial_types[block]],
                        "sequence": str(sequence),
                        "length": len(str(sequence)),
                    }
                )
        return details

    def block(self):
        """For this test, display instructions experimenter to read out to proband.
        If this is the very first trial, additionally display instructions to the
        proband.

        """
        self.first_digit_horrible_lag = True
        self.skip_countdown = True
        t = self.data.current_trial
        s = self.instructions[5 + t.block_number]
        label, btn = self.display_instructions_with_continue_button(
            s, font=QFont("Helvetica", 18)
        )

        # if very first trial, show message to proband
        if t.first_trial_in_test:
            label.hide()
            btn.hide()
            s = self.instructions[4]
            a, b = self.display_instructions_with_continue_button(s)
            b.clicked.disconnect()
            b.clicked.connect(lambda: [a.hide(), b.hide(), btn.show(), label.show()])

    def trial(self):
        """For this test, display the GUI."""
        t = self.data.current_trial

        # calculate the corect answer
        if t.block_type == "forward":
            answer = t.sequence
        elif t.block_type == "backward":
            answer = t.sequence[::-1]
        else:
            digits = []
            letters = []
            for a in t.sequence:
                if a.isdigit():
                    digits.append(a)
                elif a.isalpha():
                    letters.append(a)
            answer = sorted(digits) + sorted(letters)

        # instructions and buttons
        self.display_instructions(self.instructions[9] % "-".join(t.sequence))
        self.play_sequence(t.sequence)
        corr_button = self._display_continue_button()
        corr_button.setText(self.instructions[10] % "-".join(answer))
        corr_button.setFont(QFont("Helvetica", 18))
        corr_button.resize(corr_button.sizeHint())
        corr_button.setMinimumHeight(120)
        corr_button.setMinimumWidth(320)

        x = (self.frameGeometry().width() - corr_button.width()) // 2 - 250
        y = self.frameGeometry().height() - (corr_button.height() + 20)
        corr_button.move(x, y)
        corr_button.clicked.disconnect()
        corr_button.clicked.connect(self._correct)
        incorr_button = self._display_continue_button()
        incorr_button.setText(self.instructions[11])
        incorr_button.setFont(QFont("Helvetica", 18))
        incorr_button.resize(incorr_button.sizeHint())
        incorr_button.setMinimumHeight(120)
        incorr_button.setMinimumWidth(320)
        x = (self.frameGeometry().width() - incorr_button.width()) // 2 + 250
        y = self.frameGeometry().height() - (incorr_button.height() + 20)
        incorr_button.move(x, y)
        incorr_button.clicked.disconnect()
        incorr_button.clicked.connect(self._incorrect)

    def _correct(self):
        t = self.data.current_trial
        if t:
            t.correct = True
            t.status = "completed"
            self._add_timing_details()
            logger.info("current_trial was completed successfully")
            logger.info("(final version) of current_trial looks like %s" % str(t))
            self.next_trial()

    def _incorrect(self):
        t = self.data.current_trial
        if t:
            t.correct = False
            t.status = "completed"
            self._add_timing_details()
            logger.info("current_trial was completed successfully")
            logger.info("(final version) of current_trial looks like %s" % str(t))
            self.next_trial()

    def play_sequence(self, sequence):
        """Play the audio of a sequence."""
        sounds = []
        for g in sequence:
            p = ["L", "D"][g in "123456789"]
            sound = QSound(self.aud_stim_paths[f"SPAN-{p}{g}-V1.wav"])
            sound.play()
            while sound.isFinished():
                self.sleep(100)
            if self.first_digit_horrible_lag:
                self.sleep(200)
                self.first_digit_horrible_lag = False
            if g in [5]:
                self.sleep(1100)
            elif g in [1, 8, 9]:
                self.sleep(900)
            else:
                self.sleep(1000)

    def mousePressEvent(self, event):
        """We don't want to handle mouse presses in the same way as other tests."""
        pass

    def summarise(self):
        """See docstring for explanation."""
        dic = {}
        for kind in ["backward", "forward", "lns"]:
            trials = [
                t for t in self.data.data["completed_trials"] if t["block_type"] == kind
            ]
            dic_ = self.basic_summary(trials=trials, prefix=kind)
            trials = [t for t in trials if t["status"] == "completed"]
            trials = [t for t in trials if t["correct"]]
            if len(trials) > 0:
                dic_[kind + "_k"] = max(t["length"] for t in trials)
            else:
                dic_[kind + "_k"] = 0
            dic.update(dic_)
        return dic

    def block_stopping_rule(self):
        """Checks to see if the proband got both or all three (depending on the
        phase) sequences of the same length incorrect. If True, all sequences
        of this phase remaining in the control iterable are removed.

        """
        last_trial = self.data.completed_trials[-1]
        logger.info("applying stopping rule to this trial: %s" % str(last_trial))
        if last_trial["practice"]:
            logger.info("practice trial, so don't apply stopping rule")
            return False
        if "lns" in last_trial["block_type"]:
            logger.info("lns trial, 3 trials per length")
            n = 3
        else:
            logger.info("fwd or bwd trial, 2 trials per length")
            n = 2
        ct = self.data.completed_trials
        trials = [t for t in ct if t["block_number"] == last_trial["block_number"]]
        trials = [t for t in trials if t["length"] == last_trial["length"]]
        logger.info("%s trials to evaluate: %s" % (len(trials), trials))
        if len(trials) < n:
            logger.info("too few trials")
            return False
        errs = [t for t in trials if t["correct"] is False]
        logger.info(logger.info("%s error trials: %s" % (len(errs), errs)))
        logger.info("number of errors: %s" % len(errs))
        return True if len(errs) == n else False
