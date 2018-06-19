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

    def skip_block(self):
        """Skip the current block. This involves moving all trials with the same
        `block_number` as `current_trial` from `remaining_trials` to `completed_trials`
        and marking them all as skipped.

        """
        # shortcuts
        rts = self.remaining_trials
        cts = self.completed_trials
        ct = self.current_trial

        # find trials of current block
        indices = [rts.index(t) for t in rts if t.block_number == ct.block_number]

        # remove them one by one
        for i in indices[::-1]:
            t = rts.pop(i)
            t.skipped = True
            cts.append(t)

        # set the current trial to skipped too
        ct.skipped = True

    def abort(self):
        """End test now. This involves placing the current trial back in the
        remaining trial list and setting `test_aborted` to True.

        """
        self.test_aborted = True
        self.remaining_trials = [copy(self.current_trial)] + self.remaining_trials

    def __iter__(self):
        """Just returns itself."""
        return self

    def __next__(self):
        """Iterate over trials. This involves (1) checking whether there are any trials
        remaining, and flagging the procedure as complete if so; (2) stopping the
        iterator if the procedure is aborted or complete; and (3) moving the current
        trial to completed trials.

        """
        # any trials left?
        if len(self.remaining_trials) == 0:
            self.test_completed = True

        # stop iterator
        if self.test_aborted or self.test_completed:
            raise StopIteration

        # move trial
        if self.current_trial:

            self.completed_trials.append(copy(self.current_trial))

        # get new trial
        self.current_trial = self.remaining_trials.pop(0)

        # return the new trial
        return self.current_trial

    @property
    def any_skipped(self):
        """:obj:`bool`: Where any trials skipped?"""
        return any(t.skipped for t in self.completed_trials)
