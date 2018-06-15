"""Matrix reasoning test.

This is identical to the matrix reasoning test from the WAIS-III [1]. On each trial, the
proband sees a matrix with one missing item in the centre of the screen, and an array of
alternatives below. The task is to select the correct element from the array by clicking
within its area. There is one practice trial, which will not progress until the correct
answer is selected. The test will terminate prematurely if four out of the last five
trials were incorrect. Probands can sometimes spend minutes on single trials of this
test. To try to prevent this, each trial has a time limit. The stimuli are taken
direction from the WAIS-III.

    time_taken: time taken to complete the test (seconds).
    correct: total number of correct trials.

References:

[1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
Antonio, TX: The Psychological Corporation.

"""
from PyQt5.QtCore import QRect
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):
    def gen_control(self):
        """

        """
        answers = [
            1, 3, 1, 3, 2, 0, 0, 2, 4, 4, 4, 1, 2, 0, 1, 3, 2, 0, 0, 3, 4, 4, 1,
            1, 0, 4, 3, 2, 2, 3, 0, 3, 1, 2, 4
        ]
        return [{"trial": i, "block": i, "answer": a, "matrix": 'M%03d.png' % (i + 1),
                 "array": 'M%03da.png' % (i + 1)} for i, a in enumerate(answers)]

    def block(self):
        """

        """
        self.block_max_time = 90

        if self.data.current_trial_details['block'] == 0:
            self.display_instructions_with_continue_button(self.instructions[4])
        else:
            self.block_silent = True
            self.next_trial()

    def trial(self):
        """"""
        # clear the screen
        self.clear_screen()

        # show matrix and array
        f = self.data.current_trial_details["matrix"]
        self.matrix = self.display_image(f, (0, 125))
        f = self.data.current_trial_details["array"]
        self.array = self.display_image(f, (0, -125))

        print(self.array)
        print(self.array.frameGeometry())

        # make zones
        rects = []
        for i in range(5):
            w = int(round(self.array.frameGeometry().width() / 5))
            h = self.array.frameGeometry().height()
            x = self.array.frameGeometry().x() + w * i
            y = self.array.frameGeometry().y()
            rects.append(QRect(x, y, w, h))
        self.make_zones(rects)

        print(self.zones)

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on.

        """
        if self.doing_trial:
            if any(event.pos() in z for z in self.zones):

                # collect results
                answer = self.data.current_trial_details['answer']
                rt = self.trial_time.elapsed()
                time_elapsed = self.block_time.elapsed()
                if event.pos() in self.zones[answer]:
                    correct = True
                else:
                    correct = False
                dic = {"rt": rt, "time_elapsed": time_elapsed, "correct": correct}
                self.data.current_trial_details.update(dic)

                # apply stopping rule
                if len(self.data.results) >= 5:
                    last_five_trials = [r for r in self.data.results][:5]
                    ncorrect = len([r for r in last_five_trials if r["correct"]])
                    if ncorrect <= 4:
                        self.data.control = []
                        self.data.test_done = True

                # continue to next trial
                self.next_trial()

    def summarise(self):
        """For this test, simply take the total amount of time elapsed since starting
        the test on trial 10. Note that this is invalid if the proband did not complete
        the test in one sitting.

        """
        last_trial = self.data.results[-1]
        return {
            "time_taken": last_trial["time_elapsed"],
            "correct": len([r for r in self.data.results if r["correct"]])
        }
