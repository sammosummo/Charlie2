"""
===================
Emotion recognition
===================

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/emotionrecognition.py
:Author: Sam Mathias

Description
===========

This is a stripped-down version of the ER-40 by Gur and colleagues [1]_. On each trial,
the proband sees a colour image of a face expressing an emotion (angry or sad) or with
a neutral expression. Probands choose between the three possibilities using the arrow
keys.

Reference
=========

.. [1] Gur, R. C., Sara, R., Hagendoorn, M., Marom, O., Hughett, P., Macy L., Turner T,
  Bajcsy, R., Posner, A., & Gur, R. E.(2002). A method for obtaining 3-dimensional
  facial expressions and its standardization for use in neurocognitive studies. J.
  Neurosci. Methods, 115:137–143.

"""
from logging import getLogger
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from charlie2.tools.basetestwidget import BaseTestWidget
from charlie2.tools.stats import basic_summary

__version__ = 2.0
__author__ = "Sam Mathias"


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Hides the mouse.
            3. Set the block deadline to 300 s.

        """
        super(TestWidget, self).__init__(parent)
        self.mouse_visible = False
        if self.debugging:
            self.block_deadline = 4 * 1000
        else:
            self.block_deadline = 240 * 1000

    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        Returns:
            :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `face` (:obj:`str`)
                3. `emotion` (:obj:`str`)
        """

        def e(s):
            if "N" in s:
                return "neutral"
            if "S" in s:
                return "sad"
            if "A" in s:
                return "angry"

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
        d = [{"trial_number": i, "face": f, "emotion": e(f)} for i, f in enumerate(fs)]
        return d

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays task instructions with a key press to continue.

        """
        self.display_instructions_with_space_bar(self.instructions[4])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen (but doesn't delete).
            2. Displays the face.
            3. Displays the arrow keys and their labels.

        """
        self.clear_screen(delete=False)
        self.display_image(self.current_trial.face, (0, 100))
        self.display_keyboard_arrow_keys(self.instructions[5:8])

    def keyReleaseEvent_(self, event: QKeyEvent) -> None:
        """Key release event.

        If the event was a release of any of the three arrow keys, records a response
        and moves onto the next trial.

        Args:
            event (PyQt5.QtGui.QKeyEvent)

        """
        dic = {Qt.Key_Left: "angry", Qt.Key_Down: "neutral", Qt.Key_Right: "sad"}
        t = self.current_trial
        if event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == t.emotion
            t.status = "completed"

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Besides the basic summary stats for all trials and each emotion separately.

        Returns:
            dict: Summary statistics.

        """
        trials = self.procedure.completed_trials
        dic = basic_summary(trials)
        for emotion in ["neutral", "sad", "angry"]:
            trials_ = [t for t in trials if t["emotion"] == emotion]
            dic.update(basic_summary(trials_, prefix=emotion))
        return dic
