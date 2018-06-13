"""Test of short-term spatial memory

This test is designed to measure the capacity of spatial short-term memory. It is based
on the change-localisation task by Johnson et al. [1], but with some improvements. On
each trial, the proband sees M items, each with a random colour, position, and shape,
for 3 seconds. All items are removed for 3 seconds. The items then reappear, but half
of them have changed. The proband must click on/touch the changed items. The test is
over when the proband makes 5 errors.



"""
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from charlie2.tools.qt import ExpWidget


class Test(ExpWidget):
    def gen_control(self):
        """For this test, each potential correct click/touch is considered a trial.

        """
        names = ['block', 'trial', 'load', 'positions']
        details = []
        positions = [
            (-226, -168), (-109, 168), (217, -22), (-197, -202), (135, 101),
            (-249, 214), (-88, -159), (137, -94), (171, 7), (166, 264), (178, 172),
            (234, -251), (-241, 231), (22, -262), (-153, 174), (-95, 153), (-124, -159),
            (-12, 113), (148, -261), (209, -246), (143, -104), (237, -132), (123, -31),
            (-111, -74), (-166, 70), (-66, 160), (143, -75), (-55, 221), (135, 267),
            (6, -158), (-196, -60), (-15, -244), (14, -278), (-279, -221), (279, -186),
            (117, 181), (-147, -200), (-225, -107), (131, -258), (-97, -41), (110, 290),
            (-241, 127), (-237, -19), (261, 213), (196, 128), (-42, 188), (-66, 223),
            (87, 44), (-112, -38), (126, 228), (-75, -12), (-91, 14), (3, -258),
            (-177, -45), (95, -173), (-97, -19), (117, -28), (163, -229), (-12, 17),
            (130, -18), (8, 141), (-194, 218), (236, -289), (233, 65), (102, 116),
            (279, 278), (23, 198), (16, 18), (-69, -118), (10, 274), (-8, -62),
            (113, -177), (283, 118), (84, -91), (86, 233), (9, -199), (249, -278),
            (-212, -225), (3, 205), (95, 13), (259, 182), (-64, -54), (248, -16),
            (228, 50), (113, -151), (27, -37), (30, 227), (-171, -10), (-86, 180),
            (-43, -30), (-229, -177), (72, -158), (-110, 14), (43, 67), (211, 264),
            (218, 211), (-284, -72), (-199, 168), (-25, 43), (-143, 228), (200, 157),
            (183, 174), (-183, 267), (57, -48), (-23, 66), (239, -92), (-285, 159),
            (200, -107), (106, -234), (-208, -212), (160, 82), (232, 208), (-22, -20),
            (-220, 283), (23, 41), (24, -41), (219, -136), (7, 77), (-215, 54),
            (164, 104), (-157, 245), (-142, 275), (-241, -67), (-262, -11), (-9, -240),
            (280, -228), (-6, 53), (-249, -152), (-75, -112), (214, 224), (188, 146),
            (64, -132), (66, -70), (-274, 137), (48, -213), (140, -127), (94, -267),
            (-158, 12), (9, -6), (145, 230), (-234, 202), (19, -106), (-272, -56),
            (137, -214), (257, 63), (-194, 50), (255, -99), (189, 236), (273, -283),
            (-236, 93), (-136, 132), (-108, -3), (-187, -95), (58, -266), (-7, 35),
            (-260, 193), (47, 151), (55, -260), (60, 97), (174, -206), (70, 254),
            (-94, 183), (-183, -132), (-136, 216), (173, -234), (218, -249), (85, -146),
            (-100, 111), (52, -182), (-139, -12), (6, -137), (-130, -69), (280, 16),
            (152, 236), (27, 122), (188, -222), (-73, -70), (-257, -15), (35, -173),
            (83, -166), (205, 121), (-219, -282), (278, -282), (135, -272),
            (-214, -243), (282, -172), (-209, -167), (37, 244), (221, -119),
            (152, -125), (-29, -239), (-230, -138), (-219, -95), (95, -63),
            (120, 64), (67, 39), (3, -114), (8, -16), (55, -69), (105, -170),
            (-140, 199), (-52, -175), (250, 81), (-255, 218), (58, -136),
            (56, -167), (256, -229), (229, 174), (-199, 189), (208, -100),
            (-231, 24), (-103, 143), (-106, -134), (227, 12), (-186, -106), (-46, 82),
            (228, -116), (183, -100), (-153, -62), (-150, -13), (249, 175), (129, 129),
            (-103, 16), (-254, 69), (-213, -253), (-106, -276), (124, -163), (76, 290),
            (111, 131), (103, -216), (-184, -53), (-272, -87), (269, 156), (143, 202),
            (9, -34), (-109, -112), (-267, 151), (-157, -70), (-17, 13), (60, -259),
            (57, -163), (-27, 157), (103, 121), (-98, 93), (-50, -162), (120, -13),
            (76, -59), (-184, -259), (205, 181), (93, 161), (-271, -222), (161, 228),
            (14, -118), (282, -198), (144, 140), (-40, 262), (-77, 249), (-175, -63),
            (166, 186), (229, 125), (-113, 256), (-18, 216), (-280, 29), (211, -231),
            (-77, -199), (-170, -231), (-18, -155), (40, -281), (125, -215),
        ]
        for block in range(10):
            for trial in range(2):
                load = (block + 1) * 2
                pos = [positions.pop(0) for i in range(load)]
                details.append(dict(zip(names, [block, trial, load, pos])))
        print(len(positions))
        return details

    def block(self):
        """Simply display instructions if this is the very first block."""
        # show instructions if this is the first block
        if self.data.current_trial_details['block'] == 0:
            self.display_instructions_with_continue_button(self.instructions[4])
        else:
            self.block_silent = True  # makes other blocks silent

        print('block_silent is', self.block_silent)
        # initialise the error counter
        self.errors = 0

    def trial(self):
        """If this is the first trial in a new block, show the study stimulus."""
        # grab trial details
        t = self.data.current_trial_details['trial']
        load = self.data.current_trial_details['load']
        n = int(load / 2)
        positions = self.data.current_trial_details['positions']

        # clear the screen
        self.clear_screen()
        self.sleep(.1)

        # display the items
        self.labels = []
        for item, pos in enumerate(positions):
            label = self.display_image('l%i_t%i_i%i.png' % (load, t, item), pos)
            self.labels.append(label)
        self.sleep(.5)

        # hide the items
        [label.hide() for label in self.labels]
        self.sleep(.5)

        # replace half the items
        for item, label in enumerate(self.labels[n :]):
            s = 'l%i_t%i_i%i_r.png' % (load, t, item + n)
            pixmap = QPixmap(self.vis_stim_paths[s])
            label.setPixmap(pixmap)
            pass
        # display items again
        [label.show() for label in self.labels]

        # set up zones
        self.make_zones(l.frameGeometry() for l in self.labels)
        self.lures = self.zones[: n]
        self.targets = self.zones[n :]

        # clean up current trial details
        del self.data.current_trial_details['positions']

        # reset the correct response counter
        self.data.current_trial_details['correct'] = 0

    def mousePressEvent(self, event):
        """On mouse click/screen touch, check if it was inside an item. If so,
        the trial is over. If not, register a miss or a non-target blaze.

        """
        if self.doing_trial:

            if any(event.pos() in lure for lure in self.lures):

                self.errors += 1
                self.data.current_trial_details['errors'] = self.errors
                # remove the lure from the list
                self.lures = [t for t in self.lures if event.pos() not in t]

            elif any(event.pos() in target for target in self.targets):

                # increment the correct counter
                self.data.current_trial_details['correct'] += 1
                self.data.current_trial_details['rt'] = self.trial_time.elapsed()

                # remove the target from the list
                self.targets = [t for t in self.targets if event.pos() not in t]

                # if all found, move on to next trial
                if self.targets == []:
                    self.next_trial()
