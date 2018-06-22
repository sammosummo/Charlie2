"""
===================
verbal-fluency test
===================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/verbalfluency.py

Description
===========

Also known as the controlled oral word association test (COWAT). This test administers
the FAS-animal version [1]_ of the COWAT. First, the proband is instructed to relinquish
control of the testing computer to the experimenter. Probands are then instructed to
list as many words as they can that begin with the letter F (trial 1), A (trail 2), and
S (trial 3), or name as many animals as they can (trial 4) in 60 seconds. The
experimenter records the number of correct and incorrect responses with the GUI. There
is some controversy in the literature over whether the FAS version of the COWAT produces
similar results to the CFL version [2]_, [3]_. It would be trivial to modify this test
to include C and L trials if desired.


Summary statistics
==================

For `{x}` in [`f`, `a`, `f`, `animal`]:

* `{x}_completed` (bool): Did the proband complete the test?
* `{x}_valid` (int): Number of valid responses.
* `{x}_invalid` (int): Number of valid responses.
* `resumed` (bool): Was this test resumed at some point?


References
==========

.. [1] Spreen, O. & Strauss, E. (1998). A compendium of neuropsychological tests:
  Administration, norms and commentary. 2nd edition. Oxford University Press; New York,
  NY.

.. [2] Lacy, M. A., Gore, P. A., Pliskin, N. H., Henry, G. K., Heilbronner, R. L., &
  Hamer, D. P. (1996). Verbal fluency task equivalence. The Clinical Neuropsychologist,
  10(3), 305–308.

.. [3] Barry, D., Bates, M. E., & Labouvie, E. (2008) FAS and CFL forms of verbal
  fluency differ in difficulty: A meta-analytic study. Appl. Neuropsychol., 15(2), 97-
  106.

"""
__version__ = 2.0
__status__ = 'complete'

from PyQt5 import QtCore, QtWidgets
from charlie2.tools.testwidget import BaseTestWidget


class TestWidget(BaseTestWidget):

    def make_trials(self):
        """For this test, trial_type indicates whether it is time for the experimenter
        to provide instructions to the proband or record their responses. Kind records
        whether this is the F, A, S, or animal trial; but this is not really important
        and the letters/categories can be switched easily."""
        names = ['trial_number', 'trial_type', 'kind']
        trial_numbers = range(8)
        trial_types = ['instruct', 'perform'] * 4
        kinds = ['f'] * 2 + ['a'] * 2 + ['s'] * 2 + ['animal'] * 2
        z = zip(trial_numbers, trial_types, kinds)
        return [dict(zip(names, p)) for p in z]

    def block(self):
        """Display instructions to proband if this is the very first trial. Otherwise,
        do nothing here."""
        dpct = self.data.proc.current_trial
        self.skip_countdown = True
        if dpct.first_trial_in_test:
            self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):
        """This is kinda tricky because there are really two very different kind of
        "trials". The first simply displays some instructions that the experimenter
        reads to the proband. The second is a whole additional GUI. The two are
        implemented in separate private methods below and this method simply selects the
        correct one based on the trial_type."""
        dpct = self.data.proc.current_trial
        self.clear_screen(delete=True)
        if dpct.trial_type == "instruct":
            return self._instruct()
        else:
            return self._perform()

    def _instruct(self):
        """Just display the message."""
        dpct = self.data.proc.current_trial
        s = self.instructions[5 + dpct.trial_number // 2]
        self.display_instructions(s)
        self.display_trial_continue_button()

    def _perform(self):
        """This is the complicated bit."""
        dpct = self.data.proc.current_trial

        # set default values
        dpct.valid_responses = 0
        dpct.invalid_responses = 0
        self._time_left = 6

        # timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._tick)

        # response counter
        rsp_counter_box = QtWidgets.QGroupBox(self.instructions[13])
        rsp_counter_layout = QtWidgets.QVBoxLayout()
        self.rsp_counter = QtWidgets.QLCDNumber()
        self.rsp_counter.setDigitCount(2)
        rsp_counter_layout.addWidget(self.rsp_counter)
        rsp_counter_box.setLayout(rsp_counter_layout)

        # countdown
        countdown_box = QtWidgets.QGroupBox(self.instructions[14])
        countdown_layout = QtWidgets.QVBoxLayout()
        self.countdown = QtWidgets.QLCDNumber()
        self.countdown.setDigitCount(2)
        countdown_layout.addWidget(self.countdown)
        self.countdown.display(self._time_left)
        countdown_box.setLayout(countdown_layout)

        # response options
        response_box = QtWidgets.QGroupBox(self.instructions[10])
        response_grid = QtWidgets.QGridLayout()
        self.valid_rsp_button = QtWidgets.QPushButton(self.instructions[11])
        response_grid.addWidget(self.valid_rsp_button, 0, 0)
        self.invalid_rsp_button = QtWidgets.QPushButton(self.instructions[12])
        response_grid.addWidget(self.invalid_rsp_button, 0, 1)
        response_box_layout = QtWidgets.QVBoxLayout()
        response_box_layout.addLayout(response_grid)
        response_box.setLayout(response_box_layout)

        # start/stop button
        button_box = QtWidgets.QGroupBox(self.instructions[18])
        button_grid = QtWidgets.QGridLayout()
        self.button = QtWidgets.QPushButton(self.instructions[9])
        self.button.clicked.connect(self._start)
        button_grid.addWidget(self.button, 0, 0)
        self.quit_button = QtWidgets.QPushButton(self.instructions[19])
        self.quit_button.clicked.connect(self.next_trial)
        button_grid.addWidget(self.quit_button, 1, 0)
        self.quit_button.setEnabled(False)
        button_box_layout = QtWidgets.QVBoxLayout()
        button_box_layout.addLayout(button_grid)
        button_box.setLayout(button_box_layout)

        # layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(rsp_counter_box, 0, 0, 2, 1)
        layout.addWidget(countdown_box, 0, 1, 2, 1)
        layout.addWidget(response_box, 2, 0, 1, 2)
        layout.addWidget(button_box, 3, 0, 1, 2)
        self.setLayout(layout)

    @property
    def _total_responses(self):
        dpct = self.data.proc.current_trial
        return dpct.valid_responses + dpct.invalid_responses

    def _valid(self):
        dpct = self.data.proc.current_trial
        dpct.valid_responses += 1
        self.rsp_counter.display(self._total_responses)

    def _invalid(self):
        dpct = self.data.proc.current_trial
        dpct.valid_responses += 1
        self.rsp_counter.display(self._total_responses)

    def _start(self):
        self.timer.start(1000)
        self.button.clicked.disconnect()
        self.button.clicked.connect(self._stop)
        self.button.setText(self.instructions[15])
        self.valid_rsp_button.clicked.connect(self._valid)
        self.invalid_rsp_button.clicked.connect(self._invalid)
        self.quit_button.setEnabled(False)

    def _stop(self):
        self.timer.stop()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self._start)
        self.button.setText(self.instructions[16])
        self.valid_rsp_button.clicked.disconnect()
        self.invalid_rsp_button.clicked.disconnect()
        self.quit_button.setEnabled(True)

    def _tick(self):
        print('>>>', self.data.proc.current_trial)
        self._time_left -= 1
        self.countdown.display(self._time_left)
        if self._time_left == 0:
            self.timer.stop()
            self.data.proc.current_trial.completed = True
            self.button.clicked.disconnect()
            self.button.clicked.connect(self.next_trial)
            self.button.setText(self.instructions[17])

    def summarise(self):
        """See docstring for explanation."""
        names = {1: "f", 3: "a", 5: "s", 7: "animal"}
        dic = {}
        trials = self.data.proc.completed_trials
        for i, n in names.items():
            trial = [t for t in trials if t.trial_number == i][0]
            dic.update({
                f"{n}_completed": True,
                f"{n}_valid": trial.valid_responses,
                f"{n}_invalid": trial.invalid_responses
            })
        return dic

    def mousePressEvent(self, event):
        """We don't want to handle mouse presses in the same way as other tests."""
        pass
