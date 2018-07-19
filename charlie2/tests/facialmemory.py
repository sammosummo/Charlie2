"""
=============
Facial memory
=============

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/facialmemory.py

Description
===========

This is the first part of the Penn face memory test [1]_. In this test, the proband sees
images of faces and is asked to try to remember them. After they have seen all the
faces, they perform a recognition-memory task. Each trial comprises a face (either an
old face or a new one), and probands make old/new judgements. It is identical to the
original Penn test.


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

.. [1] Gur, R. C., Ragland, J. D., Mozley, L. H., Mozley, P. D., Smith, R., Alavi, A.,
  Bilker, W., & Gur, R. E. (1997). Lateralized changes in regional cerebral blood flow
  during performance of verbal and facial recognition tasks: Correlations with
  performance and ”effort”. Brain Cogn.,33, 388-414.

"""
__version__ = 2.0
__status__ = "production"


from logging import getLogger
from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, there are "learning" trials, followed by "recognition" trials.
        Learning trials require no input. Recognition trials can be either new or old
        trials."""
        faces = [
            ["tar%02d.png" % (i + 1) for i in range(20)],
            [
                "idis05.png",
                "tar06.png",
                "tar18.png",
                "tar11.png",
                "idis16.png",
                "tar20.png",
                "tar12.png",
                "tar16.png",
                "idis07.png",
                "idis18.png",
                "tar19.png",
                "tar02.png",
                "tar15.png",
                "idis06.png",
                "tar13.png",
                "tar10.png",
                "tar04.png",
                "idis03.png",
                "idis20.png",
                "idis19.png",
                "idis17.png",
                "tar07.png",
                "idis15.png",
                "idis09.png",
                "idis01.png",
                "idis04.png",
                "tar05.png",
                "tar14.png",
                "idis13.png",
                "idis10.png",
                "idis08.png",
                "idis11.png",
                "idis02.png",
                "tar17.png",
                "idis12.png",
                "tar01.png",
                "idis14.png",
                "tar08.png",
                "tar09.png",
                "tar03.png",
            ],
        ]
        blocks = [0, 1]
        block_types = ["learning", "recognition"]
        trialns = [20, 40]
        details = []
        for block, block_type, trialn in zip(blocks, block_types, trialns):
            for n in range(trialn):
                dic = {
                    "block_number": block,
                    "block_type": block_type,
                    "trial_number": n,
                    "face": faces[block][n],
                    "face_type": ["old", "new"]["tar" in faces[block][n]],
                }
                details.append(dic)
        return details

    def block(self):
        """The two blocks differ in terms thier duration. We use the `trial_max_time`
        trick to implement this."""
        b = self.data.current_trial.block_number
        if b == 0:
            self.trial_deadline = int(2.5 * 1000)
        else:
            self.trial_deadline = None
            self.block_deadline = 300 * 1000
        self.display_instructions_with_space_bar(self.instructions[4 + b])

    def trial(self):
        """For each trial we display a face. If a "recognition" trial, we also display
        the keyboard arrow keys."""
        self.clear_screen(delete=True)
        self.display_image(self.data.current_trial.face, (0, 100))
        b = self.data.current_trial.block_number
        if b == 1:
            s = self.instructions[2:4]
            self.keyboard_keys = self.display_keyboard_arrow_keys(s)

    def keyReleaseEvent_(self, event):
        """For this trial, listen for left- and right-arrow keyboard key presses."""
        dic = {Qt.Key_Left: "new", Qt.Key_Right: "old"}
        t = self.data.current_trial
        if t.block_number == 1 and event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == t.face_type
            t.status = "completed"

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary()
        return dic
