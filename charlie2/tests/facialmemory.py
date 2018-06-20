"""
==================
Facial-memory test
==================

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

* `completed` (bool): Did the proband complete the test successfully?
* `time_taken` (int): Time taken to complete the entire test in ms. If the test was not
  completed but at least one trial was performed, this value is the maximum time +
  the number of remaining trials multiplied by the mean reaction time over the completed
  trials.
* `responses` (int): Total number of responses.

Reference
=========

.. [1] Gur, R. C., Ragland, J. D., Mozley, L. H., Mozley, P. D., Smith, R., Alavi, A.,
  Bilker, W., & Gur, R. E. (1997). Lateralized changes in regional cerebral blood flow
  during performance of verbal and facial recognition tasks: Correlations with
  performance and ”effort”. Brain Cogn.,33, 388-414.

"""
__version__ = 2.0
__status__ = 'complete'


from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


class Test(BaseTestWidget):
    def make_trials(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        faces = [
            ["tar%02d.png" % (i + 1) for i in range(20)],
            [
                "idis05.png", "tar06.png", "tar18.png", "tar11.png", "idis16.png",
                "tar20.png", "tar12.png", "tar16.png", "idis07.png", "idis18.png",
                "tar19.png", "tar02.png", "tar15.png", "idis06.png", "tar13.png",
                "tar10.png", "tar04.png", "idis03.png", "idis20.png", "idis19.png",
                "idis17.png", "tar07.png", "idis15.png", "idis09.png", "idis01.png",
                "idis04.png", "tar05.png", "tar14.png", "idis13.png","idis10.png",
                "idis08.png", "idis11.png", "idis02.png", "tar17.png", "idis12.png",
                "tar01.png", "idis14.png", "tar08.png", "tar09.png", "tar03.png",
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
                    'trial_number': n,
                    'face': faces[block][n],
                    "face_type": ["old", "new"]["tar" in faces[block][n]],
                }
                details.append(dic)
        return details

    def block(self):
        """If first block, display instructions and set trial time limit. If second
        block, display instructions and set a different trial time limit."""
        b = self.data.proc.current_trial.block_number
        self.display_instructions_with_continue_button(self.instructions[4 + b])
        self.trial_max_time = [2.5, 15][b]


    def trial(self):
        """For this trial, cycle through trials in the first block and

        """
        dpct = self.data.proc.current_trial
        self.mouse_on = False
        self.clear_screen(delete=True)
        self.display_image(dpct.face, (0, 100))

        if dpct.block_number == 1:
            self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[2:4])

    def keyReleaseEvent(self, event):
        """For this trial, listen for left- and right-arrow keyboard key presses."""
        dic = {Qt.Key_Left: 'old', Qt.Key_Right: 'new'}

        if self.doing_trial and event.key() in dic.keys():

# record the response
response = dic[event.key()]
rt = self._trial_time.elapsed()
time_taken = self._block_time.elapsed()
correct = response == self.data.current_trial_details["face_type"]
dic = {
"response": response,
"rt": rt,
"time_taken": time_taken,
"correct": correct,
}
self.data.current_trial_details.update(dic)

# move on
self.next_trial()

    def summarise(self):
        """Simply count the number of correct trials and the time taken."""
        results = [r for r in self.data.results if r['block_type'] == 'recognition']
        return {
"time_taken": self.data.results[39]["time_taken"],
"correct": len([r for r in results if r["correct"]]),
        }
