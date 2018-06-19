"""Test of facial memory.

This is the first part of the Penn face memory test [1]. In this test, the proband sees
images of faces and is asked to try to remember them. After they have seen all the
faces, they perform a recognition-memory task. Each trial comprises a face (either an
old face or a new one), and probands make old/new judgements. It is identical to the
original Penn test.

Summary statistics:

    time_taken: time taken to complete the test (seconds).
    correct: total number of correct trials.

References:

[1] Gur, R.C., Ragland, J.D., Mozley, L.H., Mozley, P.D., Smith, R., Alavi, A., et al.
(1997). Lateralized changes in regional cerebral blood flow during performance of verbal
and facial recognition tasks: Correlations with performance and ”effort”. Brain Cogn.,
33:388-414.

"""
from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


class Test(BaseTestWidget):
    def gen_control(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        faces = [
            [
                "tar01.png",
                "tar02.png",
                "tar03.png",
                "tar04.png",
                "tar05.png",
                "tar06.png",
                "tar07.png",
                "tar08.png",
                "tar09.png",
                "tar10.png",
                "tar11.png",
                "tar12.png",
                "tar13.png",
                "tar14.png",
                "tar15.png",
                "tar16.png",
                "tar17.png",
                "tar18.png",
                "tar19.png",
                "tar20.png",
            ],
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
                    "block": block,
                    "block_type": block_type,
                    'trial': n,
                    'face': faces[block][n],
                    "face_type": ["old", "new"]["tar" in faces[block][n]],
                }
                details.append(dic)
        return details

    def block(self):
        """If this is the first block, simply display instructions. If this is the
        second block, check proband is performing at chance and quit if so.

        """
        b = self.data.current_trial_details['block']
        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # load keyobard arrow keys
        if b == 1:
            self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[2:4])

    def trial(self):
        """For this trial, show the study and test arrays, and record responses.

        """

        # grab trial details
        face = self.data.current_trial_details["face"]
        b = self.data.current_trial_details["block"]

        # prevent key presses for now
        self.hide_mouse()
        self.doing_trial = False

        # clear the screen
        self.clear_screen()

        # display the face
        self.face = self.display_image(face, (0, 100))

        # if learning trial, just display face and move on
        if b == 0:
            self.sleep(.3)
            self.next_trial()

        # if recognition trial, set up keyboard keys
        else:
            [l.show() for l in self.keyboard_keys]
            self.doing_trial = True

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
