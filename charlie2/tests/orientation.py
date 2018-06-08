"""Orientation test.

This test is designed to be administered first in any battery. On each trial,
the proband sees a red square positioned randomly on the screen. The task is to
touch the square as quickly as possible. It is similar to the mouse practice
task from [1]. There are 10 trials.

Summary statistics:

    time_taken : time taken to complete the test (seconds).

References:

[1] Gur, R.C., Ragland, D., Moberg, P.J., Turner, T.H., Bilker, W.B., Kohler,
C., Siegel, S.J., & Gur, R.E. (2001). Computerized neurocognitive scanning: I.
Methodology and validation in healthy people. Neuropsychopharmacology, 25:766-
776.

"""
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the target
        square. If so, record the trial as a success and move on.

        """

        if self.doing_trial:

            if event.pos() in self.clickable_zones[0]:

                rt = self.trial_time.elapsed()
                time_elapsed = self.test_time.elapsed()
                dic = {'rt': rt, 'time_elapsed': time_elapsed}
                self.data.current_trial_details.update(dic)
                self.square.hide()  # otherwise it will stay on the screen
                self.next_trial()

            else:

                self.data.current_trial_details['misses'] += 1

    def gen_control(self):
        """For this test, each trial simply needs its number (counting from 0)
        and the centre position of the square.

        """
        pos = [
            (-122, -53), (-40, 19), (78, -85), (251, 296), (136, -203),
            (-42, 255), (294, -221), (108, 155), (-207, -54), (95, 215)
        ]
        return [{'trial': i, 'position': p} for i, p in enumerate(pos)]

    def block(self):
        """For this test, there is only one block. There is therefore no need
        to overwrite the setup() method because everything can be done here.

        Before the first trial, we display test instructions and load pre-load
        the image of the red square (its the same on every trial).

        """
        self.display_instructions(self.instructions[4])
        self.square = self.load_image('0_s.png')

    def trial(self):
        """For this test, draw the square on the screen, and listen for a
        mouse click/screen touch within its area.

        """
        # counter for number of times proband clicks/presses elsewhere
        self.data.current_trial_details['misses'] = 0

        # move the square to the correct position
        pos = self.data.current_trial_details['position']
        g = self.move_widget(self.square, pos)

        # convert position tuple to str for healthy later storage
        self.data.current_trial_details['position'] = str(pos)

        # add the clickable zone
        self.make_clickable_zones([g], True)

    def summarise(self):
        """For this test, simply take the total amount of time elapsed since
        starting the test. Note that this is invalid if the proband did not
        complete the test in one sitting.

        """
        last_trial = self.data.results[-1]
        dic = {'time_taken': last_trial['time_elapsed']}
        return dic
