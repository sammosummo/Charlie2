"""
===========
Orientation
===========

:Status: production
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/orientation.py

Description
===========

This simple test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to press the
square as quickly as possible. It is similar to the mouse practice task from [1]_. There
are 10 trials in total and the test automatically exits after 60 s.

Summary statistics
==================

* `completed_trials` (int): Number of completed trials.
* `skipped_skipped` (int): Number of skipped trials (e.g., due to time out).
* `time_taken` (int): Time taken to complete the entire test in ms.
* `resumed` (bool): Was this test resumed at some point?
* `misses` (int): Number of presses in areas not inside the square.


Reference
=========

.. [1] Gur, R. C., Ragland, D., Moberg, P. J., Turner, T. H., Bilker, W. B., Kohler, C.,
  Siegel, S. J., & Gur, R. E. (2001). Computerized neurocognitive scanning: I.
  Methodology and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""
__version__ = 2.0
__status__ = 'production'


from logging import getLogger
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):

    def make_trials(self):
        """For this test, all we need is the trial number and position of the square on
        each trial.

        """
        pos = [(-122, -53), (-40, 19), (78, -85), (351, 296), (136, -203), (-42, 255),
               (294, -221), (308, 155), (-407, -54), (95, 215)]
        return [{"trial_number": i, "position": p} for i, p in enumerate(pos)]

    def block(self):
        """For this test, there is only one block. All we need to do is display the task
        instructions and initialise the block timeout timer.

        """
        self.block_deadline = 60 * 1000
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this test, we simply show the square to be pressed."""
        self.trial_deadline = 30 * 1000
        self.clear_screen(delete=True)
        self.procedure.current_trial.attempts = 0
        square = self.display_image("0_s.png", self.procedure.current_trial.position)
        self.make_zones([square.frameGeometry()])

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1.

        """
        if event.pos() in self.zones[0]:
            self.procedure.current_trial.correct = True
            self.procedure.current_trial.trial_status = "completed"
        else:
            self.procedure.current_trial.attempts += 1

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust_time_taken=True)
        dic["attempts"] = sum(t["attempts"] for t in self.procedure.completed_trials)
        return dic
