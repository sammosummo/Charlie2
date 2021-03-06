"""
==============
Verbal fluency
==============

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/verbalfluency.py
:Author: Sam Mathias

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
from logging import getLogger
from typing import Dict, List

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMouseEvent

from charlie2.tools.basetestwidget import BaseTestWidget
from charlie2.tools.stats import basic_summary

__version__ = 2.0
__author__ = "Sam Mathias"


logging = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self) -> List[Dict[str, int]]:
        """Generates new trials.

        Returns:
            :obj:`list`: Each entry is a dict containing:
                1. `trial_number` (:obj:`int`)
                2. `trial_type` (:obj:`str`)
                3. `kind` (:obj:`str`)

        """
        names = ["trial_number", "trial_type", "kind"]
        trial_numbers = range(8)
        trial_types = ["instruct", "perform"] * 4
        kinds = ["f"] * 2 + ["a"] * 2 + ["s"] * 2 + ["animal"] * 2
        z = zip(trial_numbers, trial_types, kinds)
        return [dict(zip(names, p)) for p in z]

    def block(self) -> None:
        """New block.

        Does the following:
            1. Displays the task instructions with a continue button.

        """
        self.skip_countdown = True
        if self.current_trial.first_trial_in_test:
            self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self) -> None:
        """New trial.

        Either called `_instruct` or `_perform`, depending on the kind of trial.

        """
        self.clear_screen(delete=True)
        if self.current_trial.trial_type == "instruct":
            return self._instruct()
        else:
            return self._perform()

    def _instruct(self) -> None:
        """Instruction trial.

        Does the following:
            1. Display instructions for the experimenter to read to the proband.

        """
        t = self.current_trial
        s = self.instructions[5 + t.trial_number // 2]
        self.display_instructions(s, font=QtGui.QFont("Helvetica", 18))
        self._add_timing_details()
        self.display_trial_continue_button()

    def _perform(self) -> None:
        """Performance trial.

        Does the following:
            1. Resents counters for responses.
            2. Sets up a timer.
            3. Sets up a response counter and countdown.
            4. Sets up experimenter buttons.
            5. Connects buttons to appropriate methods.

        """
        t = self.current_trial

        # set default values
        t.valid_responses = 0
        t.invalid_responses = 0
        self._time_left = 60

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
        self.countdown_started = False
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
        self.valid_rsp_button.setMinimumHeight(120)
        response_grid.addWidget(self.valid_rsp_button, 0, 0)
        self.valid_rsp_button.clicked.connect(self._valid)
        self.valid_rsp_button.setFont(self.instructions_font)
        self.invalid_rsp_button = QtWidgets.QPushButton(self.instructions[12])
        self.invalid_rsp_button.clicked.connect(self._invalid)
        self.invalid_rsp_button.setFont(self.instructions_font)
        self.invalid_rsp_button.setMinimumHeight(120)
        response_grid.addWidget(self.invalid_rsp_button, 0, 1)
        response_box_layout = QtWidgets.QVBoxLayout()
        response_box_layout.addLayout(response_grid)
        response_box.setLayout(response_box_layout)

        # start/stop button
        button_box = QtWidgets.QGroupBox(self.instructions[18])
        button_grid = QtWidgets.QGridLayout()
        self.button = QtWidgets.QPushButton(self.instructions[9])
        self.button.setFont(self.instructions_font)
        self.button.clicked.connect(self._start)
        self.button.setMinimumHeight(120)
        button_grid.addWidget(self.button, 0, 0)
        self.quit_button = QtWidgets.QPushButton(self.instructions[19])
        self.quit_button.setFont(self.instructions_font)
        self.quit_button.clicked.connect(self._end_trial)
        button_grid.addWidget(self.quit_button, 1, 0)
        self.quit_button.setEnabled(False)
        self.quit_button.setMinimumHeight(120)
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

        self.current_trial.responses_list = []

    @property
    def _total_responses(self) -> int:
        """Counts the total number of responses."""
        t = self.current_trial
        return t.valid_responses + t.invalid_responses

    def _valid(self) -> None:
        """Record that a valid response was made."""
        t = self.current_trial
        t.valid_responses += 1
        self.rsp_counter.display(self._total_responses)
        t.responses_list.append(("valid", self.trial_time.elapsed()))
        if self.countdown_started is False:
            self._start()

    def _invalid(self) -> None:
        """Record that a invalid response was made."""
        t = self.current_trial
        t.invalid_responses += 1
        self.rsp_counter.display(self._total_responses)
        t.responses_list.append(("invalid", self.trial_time.elapsed()))
        if self.countdown_started is False:
            self._start()

    def _start(self) -> None:
        """Start the countdown timer."""
        self.timer.start(1000)
        self.button.clicked.disconnect()
        self.button.clicked.connect(self._stop)
        self.button.setText(self.instructions[15])
        self.quit_button.setEnabled(False)
        self.countdown_started = True

    def _stop(self) -> None:
        """Pause/stop the countdown timer."""
        self.timer.stop()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self._start)
        self.button.setText(self.instructions[16])
        self.quit_button.setEnabled(True)
        self.countdown_started = False

    def _tick(self) -> None:
        """Increment the countdown timer by one second."""
        self._time_left -= 1
        self.countdown.display(self._time_left)
        if self._time_left == 0:
            self.timer.stop()
            self.current_trial.status = "completed"
            self._add_timing_details()
            logging.debug("current trial looks like %s" % str(self.current_trial))
            self.button.clicked.disconnect()
            self.button.clicked.connect(self.next_trial)
            self.button.setText(self.instructions[17])

    def _end_trial(self) -> None:
        """Record that the trial is over."""
        self.current_trial.status = "completed"
        self._add_timing_details()
        logging.debug("current trial looks like %s" % str(self.current_trial))
        self.next_trial()

    def summarise(self) -> Dict[str, int]:
        """Summarises the data.

        Besides the basic summary stats, counts the total number of attempts and errors
        redefines accuracy as correct responses divided by trials plus attempts plus
        errors. Does this separately for each of the three block types.

        Returns:
            dict: Summary statistics.

        """
        trials = self.procedure.completed_trials
        trials = [t for t in trials if t["trial_type"] == "perform"]
        dic = {"total_time_taken": basic_summary(trials)["total_time_taken"]}
        for k in ["f", "a", "s", "animal", "letter"]:
            if k != "letter":
                trials_ = [t for t in trials if t["kind"] == k]
            else:
                trials_ = [t for t in trials if t["kind"] in "fas"]
            dic.update(basic_summary(trials_, prefix=k))
            if len(trials_) > 0:
                dic["_".join((k, "valid"))] = sum(t["valid_responses"] for t in trials_)
                dic["_".join((k, "invalid"))] = sum(
                    t["invalid_responses"] for t in trials_
                )
        return dic

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Do nothing."""
        pass
