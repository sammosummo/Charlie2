"""
===================
Emotion recognition
===================

:Status: complete
:Version: 1.0
:Source: http://github.com/sammosummo/Charlie2/tests/emotionrecognition.py

Description
===========

This is a stripped-down version of the ER-40 by Gur and colleagues [1]_. On each trial,
the proband sees a colour image of a face expressing an emotion (angry or sad) or with
a neutral expression. Probands choose between the three possibilities using the arrow
keys.


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

.. [1] Gur, R. C., Sara, R., Hagendoorn, M., Marom, O., Hughett, P., Macy L., Turner T,
  Bajcsy, R., Posner, A., & Gur, R. E.(2002). A method for obtaining 3-dimensional
  facial expressions and its standardization for use in neurocognitive studies. J.
  Neurosci. Methods, 115:137–143.

"""

__version__ = 1.0
__status__ = "production"


from logging import getLogger
from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, all we need is the stimulus and the emotion gleaned from its
        filename."""
        fs = [
            "MN_223.png",
            "MSZ_112.png",
            "FAZ_32.png",
            "FN_228.png",
            "FAX_25.png",
            "MAZ_146.png",
            "MAX_39.png",
            "MAX_201.png",
            "FAZ_129.png",
            "MN_21.png",
            "FSZ_219.png",
            "MN_123.png",
            "MSX_147.png",
            "FAX_45.png",
            "FN_13.png",
            "MSZ_126.png",
            "FSZ_210.png",
            "FN_30.png",
            "MN_111.png",
            "FSX_20.png",
            "FN_204.png",
            "MSX_108.png",
            "FSX_47.png",
            "MAZ_128.png",
        ]

        def e(s):
            if "N" in s:
                return "neutral"
            if "S" in s:
                return "sad"
            if "A" in s:
                return "angry"

        d = [{"trial_number": i, "face": f, "emotion": e(f)} for i, f in enumerate(fs)]
        return d

    def block(self):
        """Simply display the task instructions."""
        self.block_deadline = 300 * 1000
        self.display_instructions_with_space_bar(self.instructions[4])
        self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[5:8])

    def trial(self):
        """For this trial, show the face and three keyboard arrow keys."""
        logger.debug("clearing screen")
        self.clear_screen(delete=False)
        logger.debug("displaying face screen")
        self.display_image(self.data.current_trial.face, (0, 100))
        logger.debug("displaying keyboard keys")
        [l.show() for l in self.keyboard_keys]

    def keyReleaseEvent_(self, event):
        """For this trial, listen for left-, down- right-arrow keyboard key presses."""
        dic = {Qt.Key_Left: "angry", Qt.Key_Down: "neutral", Qt.Key_Right: "sad"}
        t = self.data.current_trial
        if event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == t.emotion
            t.status = "completed"

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary()
        for emotion in ["neutral", "sad", "angry"]:
            trials = [
                t for t in self.data.data["completed_trials"] if t["emotion"] == emotion
            ]
            dic_ = self.basic_summary(trials=trials, prefix=emotion)
            dic.update(dic_)
        return dic
