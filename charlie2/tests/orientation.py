"""Orientation test.

This test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to touch the
square as quickly as possible. It is similar to the mouse practice task from [1]. There
are 10 trials. The test times out automatically after 30 s.

Summary statistics:

    completed (bool): Did the proband complete the test successfully?
    time_taken (int): Time taken to complete the test (ms). If the test was not
        completed but at least one trial was performed, this value is:
            30000 + number of remaining trials * mean reaction time
        If no trials were attempted, it is simply 0.
    responses (int): Total number of responses.

References:

[1] Gur, R.C., Ragland, D., Moberg, P.J., Turner, T.H., Bilker, W.B., Kohler, C.,
Siegel, S.J., & Gur, R.E. (2001). Computerized neurocognitive scanning: I.
Methodology and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, all we need is the trial number and position of the square on
        each trial.

        """
        pos = [
            (-122, -53), (-40, 19), (78, -85), (251, 296), (136, -203), (-42, 255),
            (294, -221), (108, 155), (-207, -54), (95, 215),
        ]
        return [{"trial_number": i, "position": p} for i, p in enumerate(pos)]

    def block(self):
        """For this test, there is only one block. All we need to do is display the task
        instructions and initialise the block timeout timer.

        """
        # set a timer for the block (in this case, there is only one block)
        self.block_max_time = 30

        # start the block with the task instructions
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """For this test, we simply show the square to be clicked/pressed."""
        # clear the screen
        self.clear_screen(delete=True)

        # counter for number of times the proband clicks/presses elsewhere
        self.data.proc.current_trial.misses = 0

        # show the square at the correct position
        pos = self.data.proc.current_trial.position
        self.square = self.display_image("0_s.png", pos)

        # add the square as a "zone" that can be clicked/pressed
        self.make_zones([self.square.frameGeometry()])

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the target square. If so,
        record the trial as a success and move on. If not, increase the number of
        "misses" by one.

        """
        if self.trial_on:  # only process mouse events during trials
            if event.pos() in self.zones[0]:
                self.data.proc.current_trial.rt = self._trial_time.elapsed()
                self.data.proc.current_trial.time_elapsed = self._block_time.elapsed()
                self.next_trial()
            else:
                self.data.proc.current_trial.misses += 1

    def summarise(self):
        """Summary statistics:

            completed (bool): Did the proband complete the test successfully?
            time_taken (int): Time taken to complete the test (ms). If the test was not
                completed but at least one trial was performed, this value is:
                    30000 + number of remaining trials * mean reaction time
                If no trials were attempted, it is simply 0.
                responses (int): Total number of responses.

        """
        p = self.data.proc
        if p.all_skipped:
            dic = {"completed": False, "time_taken": 0, "responses": 0}
        elif p.any_skipped:
            n = len(p.not_skipped_trials)
            xbar = int(round(sum(trial.rt for trial in p.not_skipped_trials) / n))
            dic = {
                "completed": False,
                "time_taken": 30000 + xbar * len(p.skipped_trials),
                "responses": n,
            }
        else:
            dic = {
                "completed": True,
                "time_taken": p.completed_trials[-1].time_elapsed,
                "responses": len(p.completed_trials),
            }
        return dic
