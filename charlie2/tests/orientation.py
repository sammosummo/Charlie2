"""
===========
Orientation
===========

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/orientation.py

Description
===========

This simple test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to press the
square as quickly as possible. It is similar to the mouse practice task from [1]_. There
are 20 trials in total and the test automatically times out after 60 s.

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
__status__ = "complete"


from logging import getLogger
from charlie2.tools.testwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, all we need is the trial number and position of the square on
        each trial.

        """
        pos = [(263, -23), (-190, 313), (337, -240), (399, -14), (314, 54), (-346, 186), (-104, 157), (-10, -110), (-273, 149), (-420, -197), (3, -184), (294, 1), (60, 298), (335, 73), (-7, -313), (-134, 296), (475, -241), (75, 278), (118, -139), (310, 173)]
        return [{"trial_number": i, "position": p} for i, p in enumerate(pos)]

    def block(self):
        """For this test, there is only one block. All we need to do is display the task
        instructions and initialise the block timeout timer.

        """
        self.mouse_visible = False
        self.block_deadline = 60 * 1000
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this test, we simply show the square to be pressed."""
        self.clear_screen(delete=True)
        self.data.current_trial.attempts = 0
        square = self.display_image("0_s.png", self.data.current_trial.position)
        self.make_zones([square.frameGeometry()])

    def mousePressEvent_(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase misses by 1.

        """
        if event.pos() in self.zones[0]:
            self.data.current_trial.correct = True
            self.data.current_trial.status = "completed"
        else:
            self.data.current_trial.attempts += 1

    def summarise(self):
        """See docstring for explanation."""
        dic = self.basic_summary(adjust=True)
        logger.info("changing what is meant by accuracy for this task")
        if dic["completed_trials"] > 0:
            attempts = sum(t["attempts"] for t in self.data.completed_trials)
            denom = dic["completed_trials"] + attempts
            dic["accuracy"] = dic["correct_trials"] / denom
        else:
            dic["accuracy"] = 0
        return dic
