"""Trail-making test.

In this task, the proband must click on circles drawn on the screen in a
specified order, making a 'trail' between them. There are a total of six phases
to the test, with varying numbers of trials in each phase. In the first and
second phases, the proband draws a trail between consecutive numbers, starting
with 1. In the thrid and fourth phases, the proband does the same with letters
starting with 'a'. In the fifth and sixth phases, the proband alternates
between numbers and letters. Odd-numbered phases are 'practice' phases with
8 trials each, and even-numbered phases are 'test' phases with 25 trials each.

The traditional trail-making test [1, 2] contains only two phases (equivalent
to the 'number' and 'number-letter' phases in the present version). The
traditional test is also done with pen and paper, and requires an experienced
experimenter to administer it. Thus the current version should be more
convenient than the traditional test. Please note that this test has not been
verified against the traditional version, However preliminary data from our
studies suggests that they are correlated.

Summary statistics:

    <num, let or numlet>_time_taken : time taken to complete the test phase
        (seconds).
    <num, let or numlet>_blaze_errors : number of errors inside blazes.
    <num, let or numlet>_misses : number of errors outside blazes.


References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept Mot Skills, 8:271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and
B of the Trail Making Test. J Clin Psychol, 43(4):402–409.

"""
from itertools import zip_longest
from charlie2.tools.qt import ExpWidget
from charlie2.tools.recipes import roundrobin

phases = range(0, 6)
phase_type = ('practice', 'test')
trials = [list(range(8)), list(range(25))]
blaze_positions = [
    (
        (-238, -111), (387, 60), (347, -269), (135, -157), (34, -360),
        (-227, 17), (130, 122), (400, 320),
    ),
    (
        (-264, -59), (257, 205), (-156, 238), (90, -144), (370, -146),
        (205, -348), (-209, -253), (-358, -211), (-43, -37), (122, -264),
        (-176, -359), (-139, -185), (170, 12), (400, 0), (396, 88), (347, 316),
        (-5, 172), (138, -67), (-11, -165), (211, -216), (400, -300),
        (250, -46), (-200, 101), (237, 103), (35, 329),
    ),
    (
        (-285, -22), (-44, 131), (-291, 138), (26, -219), (261, 41),
        (-324, -200), (258, -342), (191, 353),
    ),
    (
        (344, 272), (-58, 254), (-353, -329), (243, -172), (150, -400),
        (300, -309), (380, -18), (-387, -47), (-186, -385), (-189, -153),
        (361, 125), (-311, 104), (-231, 247), (-71, -192), (92, -310),
        (298, -88), (-77, 36), (98, 73), (244, 187), (33, 169), (146, 341),
        (-136, 336), (-147, 201), (-294, -102), (-33, -313),
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
numbers = list(range(1, 26))
letters = 'abcdefghijklmnopqrstuvwxy'
glyphs = [
    numbers[:8], numbers, letters[:8], letters,
    list(roundrobin(numbers[:8], letters[:8])),
    list(roundrobin(numbers, letters)),
]
details = list(
    zip_longest(phases, phase_type, trials, blaze_positions, glyphs)
)


class Test(ExpWidget):
    """Widget for the trail-making test."""

    def new_phase(self, phase):
        """Display instructions, load all blazes, show them all, and make them
        all clickable zones.

        """
        self.display_instructions(self.instructions[phase + 4])
        zones = []

        for _, _, _, pos, glyph in details[phase]:

            blaze = self.load_image(f'a_{glyph}.png')
            blaze.hide()  # otherwise it might appear
            g = self.move_widget(blaze, pos)
            zones.append(g)

        self.make_clickable_zones(zones)

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside a blaze. If so,
        the trial is over. If the last correct blaze, the phase is over.

        """

        if self.doing_trial:

            if any(event.pos() in z for z in self.clickable_zones):

                if event.pos() in self.target_blaze:

                    rt = self.trial_time.elapsed()
                    time_elapsed = self.test_time.elapsed()
                    dic = {'rt': rt, 'time_elapsed': time_elapsed}
                    self.data.current_trial_details.update(dic)
                    self.draw_trail(self.previous_blaze, self.target_blaze)

                    if self.target_blaze == self.last_target_blaze:

                        self.phase_done = True

                    self.next_trial()

                else:

                    self.data.current_trial_details['blaze_errors'] += 1

            else:

                self.data.current_trial_details['misses'] += 1

    def gen_control(self):
        """This is essentially just a flattened/expanded version of `details`
        defined outside the class.

        """
        return [list(zip_longest(list(i) for i in it)) for it in details]

    def trial(self):
        """Draw a square on the screen, define a clickable zone, and listen."""
        t = self.data.current_trial_details['trial']

        if t == 0:

            self.new_phase()
        self.data.current_trial_details['misses'] = 0
        self.data.current_trial_details['success'] = False
        n = self.data.current_trial_details['trial']
        self.square = self.load_image('%i_s.png' % (n // 2))
        pos = self.data.current_trial_details['position']
        self.square.move(*pos)
        self.data.current_trial_details['position'] = str(pos)
        self.square.show()
        self.make_clickable_zones([self.square.geometry()], True)
#
#     def summarise(self):
#         """Only one summary statistic."""
#         return {'orientation_time_taken': self.data.results[-1]['total_time']}
