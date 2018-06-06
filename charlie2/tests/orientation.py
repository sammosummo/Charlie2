"""Orientation test.

This test is designed to be administered first in any battery. On each trial,
the proband sees a red square positioned randomly on the screen. The task is to
touch the square as quickly as possible. It is similar to the mouse practice
task from [1]. There are 20 trials.

Summary statistics:

    orientation_time_taken : time taken to complete the test (seconds).

References:

[1] Gur, R.C., Ragland, D., Moberg, P.J., Turner, T.H., Bilker, W.B., Kohler,
C., Siegel, S.J., & Gur, R.E. (2001). Computerized neurocognitive scanning: I.
Methodology and validation in healthy people. Neuropsychopharmacology, 25:766-
776.

"""
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):
    """Widget for the orientation test."""

    def mousePressEvent(self, event):
        """Check if mouse press was inside the square. If so, trial is over."""
        if event.pos() in self.clickable_zones[0]:

            self.data.current_trial_details['rt'] = self.trial_time.elapsed()
            self.data.current_trial_details[
                'total_time'] = self.test_time.elapsed()
            self.data.current_trial_details['success'] = True
            self.square.hide()
            self.next_trial()

        else:

            self.data.current_trial_details['misses'] += 1

    def gen_control(self):
        """Each trial needs the trial number and position of the square."""
        pos = [
            (417, 550), (78, 547), (594, 34), (365, 369), (61, 519),
            (640, 570), (206, 511), (151, 539), (532, 271), (108, 160),
            (361, 371), (110, 306), (83, 110), (50, 398), (534, 559),
            (16, 511), (656, 309), (669, 210), (535, 564), (457, 282)
        ]
        return [{'trial': i, 'position': p} for i, p in enumerate(pos)]

    def setup(self):
        """Not much to be done."""
        # TODO: Remove this function?
        self.window_size = (800, 800)
        self.display_instructions_text('hello')

    def trial(self):
        """Draw a square on the screen, define a clickable zone, and listen."""
        self.data.current_trial_details['misses'] = 0
        self.data.current_trial_details['success'] = False
        n = self.data.current_trial_details['trial']
        self.square = self.load_image('%i_s.png' % (n // 2))
        pos = self.data.current_trial_details['position']
        self.square.move(*pos)
        self.data.current_trial_details['position'] = str(pos)
        self.square.show()
        self.make_clickable_zones([self.square.geometry()], True)

    def summarise(self):
        """Only one summary statistic."""
        return {'orientation_time_taken': self.data.results[-1]['time_taken']}
