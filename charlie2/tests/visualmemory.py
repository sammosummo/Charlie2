"""Test of short-term visual memory

This test is designed to measure the capacity of visual short-term memory for colours.
It is based on the change-localisation task by Johnson et al. [1]. On each trial, the
proband sees 5 circles, each with a random colour. All circles are removed, then
reappear, but one has changed colour. The proband must click on/touch the changed
circle. There are 30 trials, but after 10 trials, the test will start evaluating
performance and will exit early if chance performance is detected.

Summary statistics:

    time_taken: time taken to complete the test (seconds).
    correct: total number of correct trials.



"""
from math import cos, sin, pi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):
    def gen_control(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        names = ["trial", "theta"]
        thetas = [
            0.28335521,
            0.68132415,
            0.18400396,
            0.66522286,
            0.77395755,
            0.17858136,
            0.856814,
            0.1634176,
            0.57683277,
            0.24352501,
            0.26439799,
            0.42721477,
            0.0490913,
            0.11709211,
            0.61611725,
            0.11733051,
            0.13074312,
            0.34707225,
            0.13944024,
            0.83049628,
            0.18730887,
            0.16631436,
            0.26145498,
            0.28501413,
            0.93550665,
            0.5007598,
            0.52836678,
            0.42675553,
            0.49499377,
            0.78333836,
        ]
        return [dict(zip(names, params)) for params in enumerate(thetas)]

    def block(self):
        """If this is the first block, simply display instructions. If this is the
        second block, check proband is performing at chance and quit if so.

        """
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this trial, show the study and test arrays, and record responses.

        """
        # grab trial details
        trialn = self.data.current_trial_details["trial"]
        theta0 = self.data.current_trial_details["theta"] * 2 * pi

        # check for chance level
        if trialn > 10:
            ncorrect = len([r for r in self.data.results if r["correct"]])
            pcorrect = ncorrect / trialn
            if pcorrect <= .2:
                self.data.control = []
                self.data.test_done = True
                self.next_trial()
                return  # stop the current trial

        # prevent mouse clicks for now
        self.hide_mouse()
        self.doing_trial = False

        # clear the screen
        self.clear_screen()
        self.sleep(1)  # brief pause makes it less confusing when the new trial starts

        # display the items
        self.labels = []
        delta = 2 * pi / 5
        for item in range(5):
            theta = theta0 + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            label = self.display_image("l%i_t%i_i%i.png" % (5, trialn, item), (x, y))
            self.labels.append(label)
        self.sleep(3)

        # hide the items
        [label.hide() for label in self.labels]
        self.sleep(1)

        # change the target
        s = "l%i_t%i_i%i_r.png" % (5, trialn, 0)
        pixmap = QPixmap(self.vis_stim_paths[s])
        self.labels[0].setPixmap(pixmap)

        # display items again
        [label.show() for label in self.labels]

        # set up zones
        self.make_zones(l.frameGeometry() for l in self.labels)

        # set target and lures
        self.target = self.zones[0]
        self.lures = self.zones[1:]

        # allow mouse clicks again
        self.show_mouse()
        self.doing_trial = True

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the  item. If so,
        the trial is over. If not, register a miss or a non-target blaze.

        """
        if self.doing_trial:

            if any(event.pos() in z for z in self.zones):

                # record the response
                rt = self.trial_time.elapsed()
                time_taken = self.block_time.elapsed()
                if event.pos() in self.target:
                    correct = True
                else:
                    correct = False
                dic = {"rt": rt, "time_taken": time_taken, "correct": correct}
                self.data.current_trial_details.update(dic)
                self.next_trial()

    def summarise(self):
        """Simply count the number of correct trials and the time taken."""
        return {
            "time_taken": self.data.results[29]["time_taken"],
            "correct": len([r for r in self.data.results if r["correct"]]),
        }
