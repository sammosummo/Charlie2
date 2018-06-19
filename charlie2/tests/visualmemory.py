"""Test of short-term visual memory

This test is designed to measure the capacity of visual short-term memory for colours
using a change-localisation task similar to the one employed by Johnson et al. [1].
On each trial, the proband sees 5 circles, each with a random colour. All circles are
removed, then reappear, but one has changed colour. The proband must click on/touch the
changed circle. There are 30 trials, but after 5 trials, the test will start evaluating
performance and will exit early if chance performance is detected. There is a 30-s time
limit on each trial and a 240-s time limit on the whole experiment.

Summary statistics:

    completed (bool): Did the proband complete the test successfully?
    time_taken (int): Time taken to complete the test (ms). If the test was not
        completed but at least one trial was performed, this value is:
            240000 + number of remaining trials * mean reaction time
        If no trials were attempted, it is simply 0.
    correct (int): Number of correct responses.
    responses (int): Total number of responses.

References:

[1] Johnson, M.K., McMahon, R.P., Robinson, B.M., Harvey, A.N., Hahn, B., Leonard, C.J.,
Luck, S.J., & Gold, J.M. (2013). The relationship between working memory capacity and
broad measures of cognitive ability in healthy adults and people with schizophrenia.
Neuropsychol, 27(2), 220-229.

"""
from math import cos, sin, pi
from PyQt5.QtGui import QPixmap
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        names = ["trial_number", "theta"]
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
        self.trial_max_time = .15
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this trial, show the study and test arrays, and record responses.

        """
        # grab trial details
        tr = self.data.proc.current_trial.trial_number
        th = self.data.proc.current_trial.theta * 2 * pi

        # prevent mouse clicks for now
        self.hide_mouse()
        self.trial_on = False

        # clear the screen
        self.clear_screen()
        self.sleep(1)  # makes it less confusing when the new trial starts

        # display the items
        self.labels = []
        delta = 2 * pi / 5
        for item in range(5):
            theta = th + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            label = self.display_image("l%i_t%i_i%i.png" % (5, tr, item), (x, y + 75))
            self.labels.append(label)
        self.sleep(1)

        # hide the items
        [label.hide() for label in self.labels]
        self.sleep(1)

        # change the target
        s = "l%i_t%i_i%i_r.png" % (5, tr, 0)
        pixmap = QPixmap(self._vis_stim_paths[s])
        self.labels[0].setPixmap(pixmap)

        # display items again
        [label.show() for label in self.labels]
        self.display_text(self.instructions[5], (0, -225))

        # set up zones
        self.make_zones(l.frameGeometry() for l in self.labels)

        # set target and lures
        self.target = self.zones[0]
        self.lures = self.zones[1:]

        # allow mouse clicks again
        self.show_mouse()
        self.vprint('setting trial_on from test widget')
        self.trial_on = True
        print(self.trial_on)

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the  item. If so,
        the trial is over. If not, register a miss or a non-target blaze.

        """
        print(self.trial_on)
        if self.trial_on:
            if any(event.pos() in z for z in self.zones):
                self.data.proc.current_trial.rt = self._trial_time.elapsed()
                self.data.proc.current_trial.time_elapsed = self._block_time.elapsed()
                if event.pos() in self.target:
                    self.data.proc.current_trial.correct = True
                else:
                    self.data.proc.current_trial.correct = False
                self.next_trial()

    def summarise(self):
        """Summary statistics:

            completed (bool): Did the proband complete the test successfully?
            time_taken (int): Time taken to complete the test (ms). If the test was not
                completed but at least one trial was performed, this value is:
                    240000 + number of remaining trials * mean reaction time
                If no trials were attempted, it is simply 0.
            correct (int): Number of correct responses.
            responses (int): Total number of responses.
        """
        print(vars(self.data.proc))
        p = self.data.proc
        if p.all_skipped:
            dic = {"completed": False, "time_taken": 0, "correct": 0, "responses": 0}
        elif p.any_skipped:
            n = len(p.not_skipped_trials)
            xbar = int(round(sum(trial.rt for trial in p.not_skipped_trials) / n))
            dic = {
                "completed": False,
                "time_taken": 240000 + xbar * len(p.skipped_trials),
                "correct": sum(t.correct for t in p.not_skipped_trials),
                "responses": n
            }
        else:
            dic = {
                "completed": True,
                "time_taken": p.completed_trials[-1].time_elapsed,
                "correct": sum(t.correct for t in p.completed_trials),
                "responses": len(p.completed_trials)
            }
        return dic

    def stopping_rule(self):
        """After five trials completed, exit if at chance."""
        if len(self.data.proc.completed_trials) > 5:
            all_trials = self.data.proc.completed_trials
            completed = [t for t in all_trials if not t.skipped]
            correct = [t for t in completed if t.correct]
            pc = len(correct) / len(all_trials)
            return True if pc <= .2 else False
