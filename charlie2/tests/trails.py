"""Trail-making test.

In this task, the proband must click on circles drawn on the screen in a specified
order, making a 'trail' between them. There are a total of six blocks to the test, with
varying numbers of trials in each block. In the first and second blocks, the proband
draws a trail between consecutive numbers, starting with 1. In the third and fourth
blocks, the proband does the same with letters starting with 'a'. In the fifth and sixth
blocks, the proband alternates between numbers and letters. Odd-numbered blocks are
'practice' blocks with 5 trials each, and even-numbered blocks are 'test' blocks with
20 trials each.

The traditional trail-making test [1, 2] contains only two blocks (equivalent to the
'number' and 'number-letter' blocks in the present version). The traditional test is
also done with pen and paper, and requires an experienced experimenter to administer it.
Thus the current version should be more convenient than the traditional test. Please
note that this test has not been verified against the traditional version, however
preliminary data from our studies suggests that they are correlated.

Summary statistics:

    <num, let or numlet>_completed (bool): Did the proband complete the test block
        successfully?
    <num, let or numlet>_time_taken (int): Time taken to complete the test block (ms).
        If the test block was not completed but at least one trial was performed, this
        value is:
            180000 + number of remaining trials * mean reaction time
        If no trials were attempted, it is simply 0.
    <num, let or numlet>_errors (int): number of responses made inside incorrect blazes.
    <num, let or numlet>_responses (int): Total number of responses.

References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of organic
brain damage. Percept Mot Skills, 8, 271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and B of the
Trail Making Test. J Clin Psychol, 43(4), 402–409.

"""
from PyQt5.QtGui import QPainter, QPen
from charlie2.tools.recipes import charlie2_trials
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):
    def make_trials(self):
        """For this test, each trial requires the block number (for indexing the on-
        screen instructions), the block type (practice blocks are not included in the
        summary), the trial number (to indicate when a new block starts), the target
        blaze position (where a correct click/press should go), and the glyph (to load
        the correct image). All this was complicated to generate and required many
        manual edits so was all done in a different script and simply imported here.

        """
        return charlie2_trials()

    def block(self):
        """For this test, display instructions, pre-load the images, pre-move them, set
        up zones, create a painter widget for drawing the trail.

        """
        # display block-specific instructions; do this first
        b = self.data.proc.current_block_number
        self.display_instructions_with_continue_button(self.instructions[4 + b])

        # set block timeouts
        if self.data.proc.current_trial.block_type == "practice":
            self.block_max_time = 30
        else:
            self.block_max_time = 180

        # find all trials in this block
        trials = [self.data.proc.current_trial]  # bc first trial was popped
        trials += [t for t in self.data.proc.remaining_trials if t.block_number == b]

        # get their glyphs and positions
        glyphs = [t.glyph for t in trials]
        positions = [t.blaze_position for t in trials]

        # load the blazes
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
        # clear the screen but don't delete blazes
        self.clear_screen()

        # show the blazes
        [img.show() for img in self.images]

        # reset click/press counters
        self.data.proc.current_trial.misses = 0
        self.data.proc.current_trial.errors = 0

        # set target blaze
        self.target_blaze = self.rects[self.data.proc.current_trial.trial_number]

    def summarise(self):
        """Summary statistics:

            <num, let or numlet>_completed (bool): Did the proband complete the test
                block successfully?
            <num, let or numlet>_time_taken (int): Time taken to complete the test block
                (ms). If the test block was not completed but at least one trial was
                performed, this value is:
                    180000 + number of remaining trials * mean reaction time
                If no trials were attempted, it is simply 0.
            <num, let or numlet>_errors (int): number of responses made inside incorrect
                blazes.
            <num, let or numlet>_responses (int): Total number of responses.

        """
        names = {1: "num", 3: "let", 5: "numlet"}
        dic = {}

        for block, name in names.items():

            trials = self.data.proc.trials_from_block(block)
            all_skipped = all(trial.skipped for trial in trials)
            any_skipped = any(trial.skipped for trial in trials)

            if all_skipped:
                dic.update({
                    f"{name}_completed": False,
                    f"{name}_time_taken": 0,
                    f"{name}_errors": 0,
                    f"{name}_responses": 0
                })

            elif any_skipped:
                ts = [t for t in trials if not t.skipped]
                n = len([t for t in trials if t.skipped])
                rt = int(round(sum(t.rt for t in ts) / len(ts)))
                dic.update({
                    f"{name}_completed": False,
                    f"{name}_time_taken": 180 + rt * n,
                    f"{name}_errors": sum(t.errors for t in ts),
                    f"{name}_responses": len(ts),
                })

            else:
                dic.update({
                    f"{name}_completed": True,
                    f"{name}_time_taken": trials[-1].time_elapsed,
                    f"{name}_errors": sum(t.errors for t in trials),
                    f"{name}_responses": len(trials),
                })

        return dic

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside the target blaze. If so,
        the trial is over. If not, register a miss or a non-target blaze.

        """
        if self.trial_on:
            if event.pos() in self.target_blaze:
                self.data.proc.current_trial.rt = self._trial_time.elapsed()
                self.data.proc.current_trial.time_elapsed = self._block_time.elapsed()
                self.next_trial()
            elif any(event.pos() in z for z in self.zones):
                self.data.proc.current_trial.errors += 1
            else:
                self.data.proc.current_trial.misses += 1

    def paintEvent(self, event):
        """Draw a trail (straight line) from the centre of one blaze to the centre of
        the other.

        """
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(4)
        painter.setPen(pen)
        rects = self.rects[: self.data.proc.current_trial.trial_number]
        for a, b in zip([None] + rects, rects + [None]):
            if a and b:
                painter.drawLine(a.center(), b.center())
