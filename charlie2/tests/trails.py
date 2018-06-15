"""Trail-making test.

In this task, the proband must click on circles drawn on the screen in a specified
order, making a 'trail' between them. There are a total of six blocks to the test, with
varying numbers of trials in each block. In the first and second blocks, the proband
draws a trail between consecutive numbers, starting with 1. In the thrid and fourth
blocks, the proband does the same with letters starting with 'a'. In the fifth and sixth
blocks, the proband alternates between numbers and letters. Odd-numbered blocks are
'practice' blocks with 5 trials each, and even-numbered blocks are 'test' blocks with
20 trials each.

The traditional trail-making test [1, 2] contains only two blocks (equivalent to the
'number' and 'number-letter' blocks in the present version). The traditional test is
also done with pen and paper, and requires an experienced experimenter to administer it.
Thus the current version should be more convenient than the traditional test. Please
note that this test has not been verified against the traditional version, However
preliminary data from our studies suggests that they are correlated.

Summary statistics:

    <num, let or numlet>_time_taken: time taken to complete the test block
        (seconds).
    <num, let or numlet>_blaze_errors: number of errors inside blazes.
    <num, let or numlet>_misses: number of errors outside blazes.


References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of organic
brain damage. Percept Mot Skills, 8:271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and B of the
Trail Making Test. J Clin Psychol, 43(4):402–409.

"""
from PyQt5.QtGui import QPainter, QPen
from charlie2._scratch._trials import _charlie2_trials
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):
    def gen_control(self):
        """For this test, each trial requires the block number (for indexing the on-
        screen instructions), the block type (practice blocks are not included in the
        summary), the trial number (to indicate when a new block starts), the target
        blaze position (where a correct click/press should go), and the glyph (to load
        the correct image). All this was complicated to generate and required many
        manual edits so was all done in a different script and simply imported here.

        """
        return _charlie2_trials()

    def block(self):
        """For this test, display instructions, pre-load the images, pre-move them, set
        up zones, create a painter widget for drawing the trail.

        """
        # display block-specific instructions
        n = self.data.current_trial_details["block"]
        self.display_instructions_with_continue_button(self.instructions[4 + n])

        # set block timeouts
        if self.data.current_trial_details["block_type"] == "practice":
            self.block_max_time = 30
        else:
            self.block_max_time = 240

        # find all trials in this block
        trials = [self.data.current_trial_details]  # bc first trial was popped
        n = self.data.current_trial_details["block"]
        trials += [t for t in self.data.control if t["block"] == n]

        # get their glyphs and positions
        glyphs = [t["glyph"] for t in trials]
        positions = [t["blaze_position"] for t in trials]

        # display the trails
        self.rects = []
        self.images = []
        for glyph, pos in zip(glyphs, positions):
            img = self.display_image(f"a_{glyph}.png", pos)
            self.images.append(img)
            img.hide()
            self.rects.append(img.frameGeometry())

        # make zones
        self.make_zones(self.rects)

    def trial(self):
        """For this test, just listen for a mouse click within the target blaze."""
        # clear the screen and show blazes
        self.clear_screen()
        [img.show() for img in self.images]

        # reset click/press counters
        self.data.current_trial_details["misses"] = 0
        self.data.current_trial_details["blaze_errors"] = 0

        # set target blaze
        n = self.data.current_trial_details["trial"]
        self.target_blaze = self.rects[n]

        # convert position tuple to str for healthy later storage
        pos = self.data.current_trial_details["blaze_position"]
        self.data.current_trial_details["blaze_position"] = str(pos)

    def summarise(self):
        """Summary statistics:

            <num, let or numlet>_time_taken : time taken to complete the test
                block(seconds).
            <num, let or numlet>_blaze_errors : number of errors inside blazes.
            <num, let or numlet>_misses : number of errors outside blazes.

        """
        names = {1: "num", 3: "let", 5: "numlet"}
        stats = ("time_taken", "blaze_errors", "misses")
        dic = {}

        for block, name in names.items():
            try:
                results = [r for r in self.data.results if r["block"] == block][19]
                for stat in stats:
                    dic[f"{name}_{stat}"] = results[stat]
            except IndexError:
                pass
        return dic

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the target blaze. If so,
        the trial is over. If not, register a miss or a non-target blaze.

        """
        if self.doing_trial:

            if event.pos() in self.target_blaze:

                # record the response
                rt = self.trial_time.elapsed()
                time_taken = self.block_time.elapsed()
                dic = {"rt": rt, "time_taken": time_taken}
                self.data.current_trial_details.update(dic)
                self.next_trial()

            elif any(event.pos() in z for z in self.zones):

                self.data.current_trial_details["blaze_errors"] += 1

            else:

                self.data.current_trial_details["misses"] += 1

    def paintEvent(self, event):
        """Draw a trail (straight line) from the centre of one blaze to the centre of
        the other.

        """
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(4)
        painter.setPen(pen)
        rects = self.rects[: self.data.current_trial_details["trial"]]
        for a, b in zip([None] + rects, rects + [None]):
            if a and b:
                painter.drawLine(a.center(), b.center())
