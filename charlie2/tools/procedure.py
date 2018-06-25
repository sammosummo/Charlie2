"""Defines procedure classes.

"""
from copy import copy
from charlie2.tools.trial import Trial


class SimpleProcedure(object):
    def __init__(self, remaining_trials, completed_trials, current_trial, **kwargs):
        """Create a simple procedure.

        A procedure is a special iterator over trials. A "simple" procedure starts at
        the first trial and moves forward one trial at each iteration until there are
        no trials remaining or the procedure is aborted.

        Args:
            remaining_trials (`list` of :obj:`dict` or :obj:`Trial`)
            completed_trials (`list` of :obj:`dict` or :obj:`Trial`, optional)
            current_trial (:obj:`dict` or :obj:`Trial`, optional)

        """
        # parse all kwargs, add defaults if missing
        self.__dict__.update(kwargs)
        if 'test_aborted' not in self.__dict__:
            self.test_aborted = False
        if 'test_completed' not in self.__dict__:
            self.test_completed = False

        # convert dicts to trials
        self.remaining_trials = [Trial(t) for t in remaining_trials]
        self.completed_trials = [Trial(t) for t in completed_trials]
        if current_trial is not None:
            self.current_trial = Trial(current_trial)
        else:
            self.current_trial = current_trial

    def skip_current_trial(self):
        """Set the current trial to skipped.

        """
        self.current_trial.skipped = True

    def skip_block(self):
        """Set all trials within the current block to skipped, including the current
        trial.

        """
        for trial in self.remaining_trials:
            if trial.block_number == self.current_block_number:
                trial.skipped = True

    def abort(self):
        """End test now. This involves placing the current trial back in the
        remaining trial list and setting `test_aborted` to True.

        """
        self.remaining_trials = [copy(self.current_trial)] + self.remaining_trials
        self.current_trial = None
        self.test_aborted = True

    def __iter__(self):
        """Just returns itself."""
        return self

    def __next__(self):
        """Iterate over trials. This involves (1) checking whether there are any trials
        remaining, and flagging the procedure as complete if so; (2) stopping the
        iterator if the procedure is aborted or complete; and (3) moving the current
        trial to completed trials.

        """
        # move trial
        if self.current_trial and not self.test_aborted:
            self.completed_trials.append(copy(self.current_trial))

        self.current_trial = None

        # any trials left?
        if len(self.remaining_trials) == 0:
            self.test_completed = True

        # stop iterator
        if self.test_aborted or self.test_completed:
            raise StopIteration

        # get new trial
        self.current_trial = self.remaining_trials.pop(0)

        # should we skip the current trial?
        if self.current_trial.skipped:
            return self.__next__()  # recursive awesomeness!

        return self.current_trial

    @property
    def any_skipped(self):
        """:obj:`bool`: Where any trials skipped?"""
        return any(t.skipped for t in self.completed_trials)

    @property
    def all_skipped(self):
        """:obj:`bool`: Where any trials skipped?"""
        return all(t.skipped for t in self.completed_trials)

    @property
    def not_skipped_trials(self):
        """:obj:`list`: List of trials that were not skipped and not "practice" trials,
        if there were any."""
        trials = [trial for trial in self.completed_trials if not trial.skipped]
        if "block_type" in trials[0]:
            trials = [trial for trial in trials if trial.block_type != "practice"]
        return trials

    @property
    def skipped_trials(self):
        """:obj:`list`: List of trials that were skipped.and not "practice" trials,
        if there were any."""
        trials = [trial for trial in self.completed_trials if trial.skipped]
        if "block_type" in trials[0]:
            trials = [trial for trial in trials if trial.block_type != "practice"]
        return trials

    @property
    def current_block_number(self):
        """:obj:`int`: Block number of current trial."""
        return self.current_trial.block_number

    def trials_from_block(self, bn):
        """Return all completed trials from a given block."""
        return [trial for trial in self.completed_trials if trial.block_number == bn]



