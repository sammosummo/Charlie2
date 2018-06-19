"""Emotion-recognition test

This is a stripped-down version of the ER40 by Gur and colleagues [1]. On each trial,
the proband sees a colour image of a face expressing an emotion (angry or sad) or with
a neutral expression. Probands make their responses using the arrow keys.

Summary statistics:

    time_taken: time taken to complete the test (seconds).
    correct: total number of correct trials.

References:

[1] Gur, R.C., Sara, R., Hagendoorn, M., Marom, O., Hughett, P., Macy L., et al. (2002).
A method for obtaining 3-dimensional facial expressions and its standardization for use
in neurocognitive studies. J. Neurosci. Methods, 115:137–143.

"""
from PyQt5.QtCore import Qt
from charlie2.tools.testwidget import BaseTestWidget


class Test(BaseTestWidget):
    def gen_control(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        faces = [
            'MN_223.png', 'MSZ_112.png', 'FAZ_32.png', 'FN_228.png', 'FAX_25.png',
            'MAZ_146.png', 'MAX_39.png', 'MAX_201.png', 'FAZ_129.png', 'MN_21.png',
            'FSZ_219.png', 'MN_123.png', 'MSX_147.png', 'FAX_45.png', 'FN_13.png',
            'MSZ_126.png', 'FSZ_210.png', 'FN_30.png', 'MN_111.png', 'FSX_20.png',
            'FN_204.png', 'MSX_108.png', 'FSX_47.png', 'MAZ_128.png'
        ]

        def emot(s):
            if 'N' in s: return 'neutral'
            if 'S' in s: return 'sad'
            if 'A' in s: return 'angry'

        return [{'trial': i, 'face': f, 'emotion': emot(f)} for i, f in
                enumerate(faces)]

    def block(self):
        """

        """
        self.display_instructions_with_continue_button(self.instructions[4])
        self.keyboard_keys = self.load_keyboard_arrow_keys(self.instructions[5:8])

    def trial(self):
        """For this trial, show the face and record responses.

        """
        self.hide_mouse()

        # clear the screen
        self.clear_screen()

        # display the face
        f = self.data.current_trial_details['face']
        self.face = self.display_image(f, (0, 100))

        # display keyboard keys
        [l.show() for l in self.keyboard_keys]

    def keyReleaseEvent(self, event):
        """For this trial, listen for left- and right-arrow keyboard key presses."""
        dic = {Qt.Key_Left: 'angry', Qt.Key_Down: 'neutral', Qt.Key_Right: 'sad'}

        if self.trial_on and event.key() in dic.keys():

            # record the response
            response = dic[event.key()]
            rt = self.trial_time.elapsed()
            time_taken = self.block_time.elapsed()
            correct = response == self.data.current_trial_details["emotion"]
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
        return {
            "time_taken": self.data.results[23]["time_taken"],
            "correct": len([r for r in self.data.results if r["correct"]]),
        }
