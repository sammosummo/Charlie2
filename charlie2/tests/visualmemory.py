"""
==================
Visual-memory test
==================

:Status: complete
:Version: 1.0
:Source: http://github.com/sammosummo/Charlie2/tests/visualmemory.py

Description
===========

This test is designed to measure the capacity of visual short-term memory for colours
using a change-localisation task similar to the one employed by [1]_. On each trial, the
proband sees 5 circles, each with a random colour. All circles are removed, then
reappear, but one has changed colour. The proband must click on/touch the changed
circle. There are 30 trials, but after 5 trials, the test will start evaluating
performance and will quit early if chance performance is detected. There is a 30-second
time limit on each trial and a 240-second time limit on the whole experiment.


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

.. [1] Johnson, M. K., McMahon, R. P., Robinson, B. M., Harvey, A. N., Hahn, B.,
  Leonard, C. J., Luck, S. J., & Gold, J. M. (2013). The relationship between working
  memory capacity and broad measures of cognitive ability in healthy adults and people
  with schizophrenia. Neuropsychol, 27(2), 220-229.

"""
__version__ = 1.0
__status__ = 'complete'


from math import cos, sin, pi
from PyQt5.QtGui import QPixmap
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        names = ["trial_number", "theta"]
        thetas = [
            0.28335521, 0.68132415, 0.18400396, 0.66522286, 0.77395755, 0.17858136,
            0.856814, 0.1634176, 0.57683277, 0.24352501, 0.26439799, 0.42721477,
            0.0490913, 0.11709211, 0.61611725, 0.11733051, 0.13074312, 0.34707225,
            0.13944024, 0.83049628, 0.18730887, 0.16631436, 0.26145498, 0.28501413,
            0.93550665, 0.5007598, 0.52836678, 0.42675553, 0.49499377, 0.78333836,
        ]
        return [dict(zip(names, params)) for params in enumerate(thetas)]

    def block(self):
        """If this is the first block, simply display instructions."""
        self.trial_max_time = 15
        self.block_max_time = 240
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this trial, show the study and test arrays, and record responses."""
        dpct = self.data.proc.current_trial

        # prevent mouse clicks for now
        self.mouse_on = False
        self.trial_on = False

        # clear the screen
        self.clear_screen()
        self.sleep(1)  # makes it less confusing when the new trial starts

        # display the items
        self.labels = []
        delta = 2 * pi / 5
        for item in range(5):
            theta = dpct.theta * 2 * pi + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            s = "l%i_t%i_i%i.png" % (5, dpct.trial_number, item)
            label = self.display_image(s, (x, y + 75))
            self.labels.append(label)
        self.sleep(1.5)

        # hide the items
        [label.hide() for label in self.labels]
        self.sleep(1)

        # change the target
        s = "l%i_t%i_i%i_r.png" % (5, dpct.trial_number, 0)
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
        self.mouse_on = True
        self.trial_on = True

    def summarise(self):
        """See docstring for explanation."""
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

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the correct item."""
        dpct = self.data.proc.current_trial
        dpct.correct = event.pos() in self.target
        dpct.completed = any(event.pos() in z for z in self.zones)

    def stopping_rule(self):
        """After five trials completed, exit if at chance."""
        if len(self.data.proc.completed_trials) > 5:
            all_trials = self.data.proc.completed_trials
            completed = [t for t in all_trials if not t.skipped]
            correct = [t for t in completed if t.correct]
            pc = len(correct) / len(all_trials)
            return True if pc <= .2 else False
