"""Trail-making test.

In this task, the proband must click on circles drawn on the screen in a
specified order, making a 'trail' between them. There are a total of six trials
in the test, distributed over three phases. In the first phase, the proband
draws trails between consecutive numbers, starting with 1. In the second phase,
the proband does the same with letters starting with a. In the third phase, the
proband alternates between numbers and letters. Each phase contains a practice
trial with 8 circles, and test trial with 25 circles.

The traditional trail-making test [1, 2] contains only two phases (equivalent
to the 'number' and 'number-letter' phases in the present version). The
traditional test is also done with pen and paper, and requires an experienced
experimenter to administer it. Thus the current version should be more
convenient than the traditional test.

Please note that this test has not yet been verified against the pen-and-paper
trail-making test. However, preliminary data from our study suggests that they
are correlated.

Summary statistics:

    trails_<trial>_time_taken : time taken to complete the trial (seconds).
    trails_<trial>_blaze_errors : number of errors inside blazes.
    trails_<trial>_nonblaze_errors : number of errors outside blazes.


References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept Mot Skills, 8:271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and
B of the Trail Making Test. J Clin Psychol, 43(4):402–409.

"""
from charlie2.tools.qt import ExpWidget
from charlie2.tools.misc import roundrobin


class Test(ExpWidget):
    """Widget for the orientation test."""

    def mousePressEvent(self, event):
        """Check if mouse press was inside the correct blaze. If this was the
        last blaze, the trial is over."""

        if self.doing_trial:

            if any(event.pos() in z for z in self.clickable_zones):

                if event.pos() in self.target_blaze:

                    self.data.current_trial_details[
                        'rt'] = self.trial_time.elapsed()
                    self.data.current_trial_details[
                        'total_time'] = self.test_time.elapsed()

                    if self.target_blaze == self.last_target_blaze:

                        self.next_trial()

                else:

                    self.data.current_trial_details['blaze_errors'] += 1

            else:

                self.data.current_trial_details['nonblaze_errors'] += 1

    def gen_control(self):
        """Each trial needs the trial number and position of the square."""
        pos = [
            (
                (-238, -111), (387, 60), (347, -269), (135, -157),
                (34, -360), (-227, 17), (130, 122), (400, 320),
            ),
            (
                (-264, -59), (257, 205), (-156, 238), (90, -144), (370, -146),
                (205, -348), (-209, -253), (-358, -211), (-43, -37),
                (122, -264), (-176, -359), (-139, -185), (170, 12), (400, 0),
                (396, 88), (347, 316), (-5, 172), (138, -67), (-11, -165),
                (211, -216), (400, -300), (250, -46), (-200, 101), (237, 103),
                (35, 329),
             ),
            (
                (-285, -22), (-44, 131), (-291, 138), (26, -219),
                (261, 41), (-324, -200), (258, -342), (191, 353),
            ),
            (
                (344, 272), (-58, 254), (-353, -329), (243, -172), (150, -400),
                (300, -309), (380, -18), (-387, -47), (-186, -385),
                (-189, -153), (361, 125), (-311, 104), (-231, 247),
                (-71, -192), (92, -310), (298, -88), (-77, 36), (98, 73),
                (244, 187), (33, 169), (146, 341), (-136, 336), (-147, 201),
                (-294, -102), (-33, -313),
             ),
            (
                (337, 13), (-345, -3), (396, 280), (-365, 118), (86, -231),
                (-306, -275), (366, -125), (-165, -131),
            ),
            (
                (-316, -140), (-385, 6), (-387, -346), (296, -328), (303, -57),
                (308, 252), (361, 23), (127, 30), (-266, -64), (-166, -64),
                (193, -217), (-88, 123), (178, 213), (353, -240), (-27, -399),
                (-65, -228), (-248, 58), (-33, 270), (-371, 180), (-205, -274),
                (60, -276), (-132, 28), (76, 101), (91, 346), (-126, 345),
            ),
        ]
        phases = ['practice', 'test'] * 3
        numbers = list(range(1, 26))
        letters = 'abcdefghijklmnopqrstuvwxy'
        seq = list(roundrobin(numbers, letters))

        glyphs = [numbers[: 8], numbers, letters[: 8], ]
        return [{'trial': i, 'position': p} for i, p in enumerate(pos)]

    def setup(self):
        """Not much to be done."""
        # TODO: Remove this function?
        self.window_size = (800, 800)
        self.display_instructions(self.instructions[4])

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
        return {'orientation_time_taken': self.data.results[-1]['total_time']}
