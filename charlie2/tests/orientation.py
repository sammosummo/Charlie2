"""
================
Orientation test
================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/orientation.py

Description
===========

This simple test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to touch the
square as quickly as possible. It is similar to the mouse practice task from [1]_. There
are 10 trials in total and the test automatically quits after 30 s.

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

.. [1] Gur, R. C., Ragland, D., Moberg, P. J., Turner, T. H., Bilker, W. B., Kohler, C.,
  Siegel, S. J., & Gur, R. E. (2001). Computerized neurocognitive scanning: I.
  Methodology and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""
__version__ = 2.0
__status__ = 'complete'


from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):

    def make_trials(self):
        """For this test, all we need is the trial number and position of the square on
        each trial."""
        pos = [(-122, -53), (-40, 19), (78, -85), (251, 296), (136, -203), (-42, 255),
               (294, -221), (108, 155), (-207, -54), (95, 215)]
        return [{"trial_number": i, "position": p} for i, p in enumerate(pos)]

    def block(self):
        """For this test, there is only one block. All we need to do is display the task
        instructions and initialise the block timeout timer."""
        self.block_max_time = 30
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this test, we simply show the square to be clicked/pressed."""
        dpct = self.data.proc.current_trial
        self.clear_screen(delete=True)
        dpct.misses = 0
        pos = dpct.position
        self.square = self.display_image("0_s.png", pos)
        self.make_zones([self.square.frameGeometry()])

    def summarise(self):
        """See docstring for explanation."""
        dp = self.data.proc
        if dp.all_skipped:
            dic = {"completed": False, "time_taken": 0, "responses": 0}
        elif dp.any_skipped:
            n = len(dp.not_skipped_trials)
            xbar = int(round(sum(trial.rt for trial in dp.not_skipped_trials) / n))
            dic = {
                "completed": False,
                "time_taken": 30000 + xbar * len(dp.skipped_trials),
                "responses": n,
            }
        else:
            dic = {
                "completed": True,
                "time_taken": dp.completed_trials[-1].time_elapsed,
                "responses": len(dp.completed_trials),
            }
        return dic

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1."""
        dpct = self.data.proc.current_trial
        if event.pos() in self.zones[0]:
            dpct.completed = True
        else:
            dpct.misses += 1
