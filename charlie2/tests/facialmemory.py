"""
=============
Facial memory
=============

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/facialmemory.py
:Author: Sam Mathias

Description
===========

This is the first part of the Penn face memory test [1]_. In this test, the proband sees
images of faces and is asked to try to remember them. After they have seen all the
faces, they perform a recognition-memory task. Each trial comprises a face (either an
old face or a new one), and probands make old/new judgements. It is identical to the
original Penn test.

Reference
=========

.. [1] Gur, R. C., Ragland, J. D., Mozley, L. H., Mozley, P. D., Smith, R., Alavi, A.,
  Bilker, W., & Gur, R. E. (1997). Lateralized changes in regional cerebral blood flow
  during performance of verbal and facial recognition tasks: Correlations with
  performance and ”effort”. Brain Cogn.,33, 388-414.

"""
from logging import getLogger
from sys import gettrace
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from charlie2.tools.basetestwidget import BaseTestWidget

from ..tools.stats import basic_summary

__version__ = 2.0
__author__ = "Sam Mathias"


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def __init__(self, parent=None) -> None:
        """Initialise the test.

        Does the following:
            1. Calls super() to initialise everything from base classes.
            2. Hides the mouse.
            3. Loads the keyboard arrow keys.

        """
        super(TestWidget, self).__init__(parent)
        self.mouse_visible = False
        self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[2:4])

    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        Returns:
            :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `block_number` (:obj:`int`)
                3. `block_type` (:obj:`str`)
                4. `face` (:obj:`str`)
                5. `face_type` (:obj:`str`)

        """
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

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays block-specific task instructions with a key press to continue.
            2. Changes the trial deadline based on block type.

        """
        b = self.current_trial.block_number
        if b == 0:
            if self.debugging is False:
                self.trial_deadline = int(2.5 * 1000)
            else:
                self.trial_deadline = 100
        else:
            self.trial_deadline = None
            if self.debugging:
                self.block_deadline = 4 * 1000
            else:
                self.block_deadline = 240 * 1000
        self.display_instructions_with_space_bar(self.instructions[4 + b])

    def trial(self) -> None:
        """New trial.

        Does the following:
            1. Clears the screen.
            2. Displays the face.
            3. Displays the arrow keys and their labels, if during recognition phase.

        """
        self.clear_screen(delete=True)
        self.display_image(self.current_trial.face, (0, 100))
        b = self.current_trial.block_number
        if b == 1:
            self.display_keyboard_arrow_keys(self.instructions[2:4])

    def keyReleaseEvent_(self, event: QKeyEvent) -> None:
        """Key release event.

        If the event was a release of either the left or right arrow keys, records a
        response and moves onto the next trial.

        Args:
            event (PyQt5.QtGui.QKeyEvent)

        """
        dic = {Qt.Key_Left: "new", Qt.Key_Right: "old"}
        t = self.current_trial
        if t.block_number == 1 and event.key() in dic:
            t.rsp = dic[event.key()]
            t.correct = t.rsp == t.face_type
            t.status = "completed"

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Performs a basic summary on trials from the recognition phase only.

        Returns:
            dict: Summary statistics.

        """
        trials = [
            t
            for t in self.procedure.completed_trials
            if t["block_type"] == "recognition"
        ]
        return basic_summary(trials)
