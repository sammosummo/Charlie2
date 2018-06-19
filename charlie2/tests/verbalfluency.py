"""Controlled oral word association test (COWAT)

This test administers the FAS version [1] of the COWAT. First, the proband is instructed
to relinquish control of the testing computer to the experimenter. Probands are then
instructed to list as many words as they can that begin with the letter F (trial 1),
A (trail 2), and S (trial 3), or name as many animals as they can (trial 4) in 60
seconds. The experimenter records the number of correct and incorrect responses. With
the GUI. There is some controversy in the literature over whether the FAS version of the
COWAT produces similar results to the CFL version [2, 3]. It would be trivial to modify
this test to include C and L trials if desired.

Summary statistics:

    <f, a, s, or animal>_valid: number of valid responses
    <f, a, s, or animal>_invalid: number of valid responses
References:

[1] Spreen, O. & Strauss, E. (1998). A compendium of neuropsychological tests:
Administration, norms and commentary. 2nd edition. Oxford University Press; New York,
NY.

[2] Lacy, M.A., Gore, P.A., Pliskin, N.H., Henry, G.K., Heilbronner, R.L., & Hamer, D.P.
(1996). Verbal fluency task equivalence. The Clinical Neuropsychologist, 10(3):305–308.

[3] Barry, D., Bates, M.E., & Labouvie, E. (2008) FAS and CFL forms of verbal fluency
differ in difficulty: A meta-analytic study. Appl. Neuropsychol., 15(2): 97-106.

"""
from PyQt5 import QtCore, QtWidgets
from charlie2.tools.testwidget import BaseTestWidget


class Test(BaseTestWidget):

    def gen_control(self):
        names = ['trial', 'trial_type']
        trial_types = ['instruct', 'test'] * 3
        return [dict(zip(names, p)) for p in enumerate(trial_types)]

    def block(self):
        self.skip_countdowns = True
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        print('>>>', self.data.current_trial_details)
        if self.data.current_trial_details['trial_type'] == 'instruct':
            print('>>> instruct')
            self.display_instructions_with_continue_button('')
        # self.next_trial()
    #     self.clear_screen()
    #
    #     if self.data.current_trial_details['trial_type'] == 'instruct':
    #
    #         t = self.data.current_trial_details['trial']
    #         s = self.instructions[5 + t // 2]
    #         self.display_instructions_with_continue_button(s)
    #
    #     else:
    #
    #         # draw the gui
    #         response_box = QtWidgets.QGroupBox(self.instructions[8])
    #         response_grid = QtWidgets.QGridLayout()
    #         self.valid_rsp_button = QtWidgets.QPushButton(self.instructions[9])
    #         response_grid.addWidget(self.valid_rsp_button, 1, 1)
    #         self.valid_rsp_button.clicked.connect(self.valid_response)
    #         self.invalid_rsp_button = QtWidgets.QPushButton(self.instructions[10])
    #         response_grid.addWidget(self.invalid_rsp_button, 1, 2)
    #         self.invalid_rsp_button.clicked.connect(self.invalid_response)
    #         response_box_layout = QtWidgets.QVBoxLayout()
    #         response_box_layout.addLayout(response_grid)
    #         response_box.setLayout(response_box_layout)
    #         rsp_counter_box = QtWidgets.QGroupBox(self.instructions[11])
    #         rsp_counter_layout = QtWidgets.QVBoxLayout()
    #         self.rsp_counter = QtWidgets.QLCDNumber()
    #         self.rsp_counter.setDigitCount(2)
    #         rsp_counter_layout.addWidget(self.rsp_counter)
    #         rsp_counter_box.setLayout(rsp_counter_layout)
    #         countdown_box = QtWidgets.QGroupBox(self.instructions[12])
    #         countdown_layout = QtWidgets.QVBoxLayout()
    #         self.countdown = QtWidgets.QLCDNumber()
    #         self.countdown.setDigitCount(2)
    #         countdown_layout.addWidget(self.countdown)
    #         countdown_box.setLayout(countdown_layout)
    #         layout = QtWidgets.QHBoxLayout()
    #         layout.addWidget(response_box)
    #         layout.addWidget(rsp_counter_box)
    #         layout.addWidget(countdown_box)
    #         self.button = QtWidgets.QPushButton()
    #         layout2 = QtWidgets.QVBoxLayout()
    #         layout2.addLayout(layout)
    #         layout2.addWidget(self.button)
    #         self.setLayout(layout2)
    #         self.rsp_counter.display(self.responses_made)
    #         self.countdown.display(self.seconds_left)
    #
    #         # containers for responses
    #         self.responses_made = 0
    #
    # def valid_response(self):
    #     self.response(True)
    #
    # def invalid_response(self):
    #     self.response(False)
    #
    # def response(self, valid):
    #     self.responses_made += 1
    #     self.rsp_counter.display(self.responses_made)
    #
    #     if not self.countdown_over and not self.countdown_began:
    #
    #         self.timer = QtCore.QTimer()
    #         self.timer.start(1000)
    #         self.button.setText(self.instructions[13])
    #         try:
    #             self.button.clicked.disconnect()
    #         except TypeError:
    #             pass
    #         self.button.clicked.connect(self.pause_timer)
    #         self.countdown.display(self.seconds_left)
    #         self.countdown_began = True
    #
    # def timerEvent(self, _):
    #
    #     if self.seconds_left > 0:
    #         self.seconds_left -= 1
    #         self.countdown.display(self.seconds_left)
    #     else:
    #         self.timer.stop()
    #         self.countdown_over = True
    #         self.button.setText(self.instructions[14])
    #         try:
    #             self.button.clicked.disconnect()
    #         except TypeError:
    #             pass
    #         self.button.clicked.connect(self.next_trial)
    #
    # def pause_timer(self):
    #     if self.timer.isActive():
    #         self.timer.stop()
    #         self.button.setText(self.instructions[14])
    #         try:
    #             self.button.clicked.disconnect()
    #         except TypeError:
    #             pass
    #         self.button.clicked.connect(self.next_trial)
    #         self.countdown_began = False