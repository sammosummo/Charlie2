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

Reference
=========

.. [1] Gur, R. C., Ragland, D., Moberg, P. J., Turner, T. H., Bilker, W. B., Kohler, C.,
  Siegel, S. J., & Gur, R. E. (2001). Computerized neurocognitive scanning: I.
  Methodology and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""
__version__ = 2.0


from logging import getLogger
from charlie2.tools.basetestwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):

    def __init__(self, parent=None):

        super(TestWidget, self).__init__(parent)

    def make_trials(self):

        pos = [
            (263, -23),
            (-190, 313),
            (337, -240),
            (399, -14),
            (314, 54),
            (-346, 186),
            (-104, 157),
            (-10, -110),
            (-273, 149),
            (-420, -197),
            (3, -184),
            (294, 1),
            (60, 298),
            (335, 73),
            (-7, -313),
            (-134, 296),
            (475, -241),
            (75, 278),
            (118, -139),
            (310, 173),
        ]
        return [{"trial_number": i, "position": p} for i, p in enumerate(pos)]

    def block(self):

        self.block_deadline = 60 * 1000
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):

        self.clear_screen(delete=True)
        self.data.current_trial.attempts = 0
        square = self.display_image("0_s.png", self.data.current_trial.position)
        self.make_zones([square.frameGeometry()])

    def mousePressEvent_(self, event):

        if event.pos() in self.zones[0]:
            self.data.current_trial.correct = True
            self.data.current_trial.status = "completed"
        else:
            self.data.current_trial.attempts += 1

    def summarise(self):

        dic = self.basic_summary(adjust=True)
        logger.info("changing what is meant by accuracy for this task")
        if dic["completed_trials"] > 0:
            trials = [t for t in self.data.completed_trials if "attempts" in t]
            attempts = sum(t["attempts"] for t in trials)
            dic["attempts"] = attempts
            denom = dic["completed_trials"] + attempts
            dic["accuracy"] = dic["correct_trials"] / denom
        else:
            dic["accuracy"] = 0
            dic["attempts"] = 0
        return dic
