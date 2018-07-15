"""Defines  custom data structures.

"""
from datetime import datetime
from getpass import getuser
from logging import getLogger
from os.path import exists, join as pj
from pickle import load, dump
from socket import gethostname
from .paths import proband_path, test_data_path


logger = getLogger(__name__)
forbidden_ids = {"TEST", ""}
this_user = getuser()
this_computer = gethostname()


class Trial(dict):
    def __init__(self, *args, **kwds):
        """Create a trial object.

        Trials objects are fancy dictionaries whose items are also attributes. They are
        initialised exactly like dictionaries except that the resulting object must
        contain the attribute `'trial_number'`. Trials typically contain several other
        attributes in addition to those listed below. Trials from the same experiment
        should contain the same attributes.

        """
        super(Trial, self).__init__(*args, **kwds)
        self.__dict__ = self
        logger.info("trial object created")

        logger.info("checking the trial object contains trial_number")
        assert "trial_number" in self.__dict__, "must contain 'trial_number'"
        assert isinstance(self.trial_number, int), "'trial_number' must be an int"

        logger.info("adding default attributes")
        defaults = {
            "block_number": 0, "trial_status": "pending","practice_trial": False
        }
        for k, v in defaults.items():
            if k not in self.__dict__:
                self.__dict__[k] = v
        if self.block_number == 0:
            self.__dict__["first_block"] = True
        else:
            self.__dict__["first_block"] = False
        if self.trial_number == 0:
            self.__dict__["first_trial_in_block"] = True
        else:
            self.__dict__["first_trial_in_block"] = False
        if self.first_block and self.first_trial_in_block:
            self.__dict__["first_trial_in_test"] = True
        else:
            self.__dict__["first_trial_in_test"] = False
        logger.info("finished constructing trial")


class ProbandData:
    def __init__(self, **kwds):
        """Create a proband data object.

        These objects contain information about the current proband, such as their ID,
        when they were tested, etc. This information is saved in a special .pkl file
        (really just a pickled python dictionary). When the object is initialised, it
        will try to load any pre-existing information about the proband, which can be
        overwritten if necessary.

        """
        logger.info("initialising a ProbandData object with kwds: %s" % str(kwds))
        self.data = {}
        self.data.update(kwds)
        if "proband_id" not in kwds:
            logger.info("no proband_id, assuming 'TEST'")
            self.data["proband_id"] = "TEST"
        self.data["current_computer_id"] = this_computer
        self.data["current_user_id"] = this_user
        self.data["filename"] = self.data["proband_id"] + ".pkl"
        self.data["path"] = pj(proband_path, self.data["filename"])
        self.update()
        self.load()
        logger.info("after fully initialising, object looks like this: %s" % self.data)

    def load(self):
        """Load pre-existing data (and update current data) if any exist."""
        logger.info("called load()")
        if exists(self.path):
            logger.info("file exists")
            prev_data = load(open(self.path, "rb"))
            self.data.update(prev_data)
            self.data["previous_computer_id"] = prev_data["current_computer_id"]
            self.data["previous_user_id"] = prev_data["current_user_id"]
            self.data["last_loaded"] = datetime.now()
            self.data["current_computer_id"] = this_computer
            self.data["current_user_id"] = this_user
        else:
            logger.info("file does not exist")
            self.data["created"] = datetime.now()
            self.data["original_computer_id"] = this_computer
            self.data["original_user_id"] = this_user
        logger.info("current data file updated to %s" % self.data)
        self.update()

    def save(self):
        """Dump the data. Don't do this if proband ID is TEST."""
        logger.info("called save()")
        if self.proband_id.upper() not in forbidden_ids:
            logger.info("saving the data")
            self.data["saved"] = datetime.now()
            dump(self.data, open(self.path, "wb"))
            self.update()
        else:
            logger.info("not saving the data (forbidden ID)")

    def update(self):
        """Updates the attributes according to the internal dictionary."""
        self.__dict__.update(self.data)


class TestData(ProbandData):
    def __init__(self, **kwds):
        """Create a test data object.

        Similar to ProbandData but for individual tests. Contains all the necessary
        information for a proband to perform/resume a test, and to calculate summary
        statistics. This information is saved in a special .pkl file (really just a
        pickled python dictionary). When the object is initialised, it will try to load
        any pre-existing information about the proband, which can be overwritten if
        necessary.

        """
        logger.info("initialising a TestData object with kwds: %s" % str(kwds))
        assert "test_name" in kwds, "Missing test_name keyword argument"
        logger.info("initialising (and saving) a corresponding ProbandData object")
        ProbandData(**kwds).save()

        self.data = {}
        self.data.update(kwds)
        if "proband_id" not in kwds:
            logger.info("no proband_id, assuming 'TEST'")
            self.data["proband_id"] = "TEST"
        self.data["current_computer_id"] = this_computer
        self.data["current_user_id"] = this_user
        self.data["filename"] = (
            self.data["proband_id"] + "_" + self.data["test_name"] + ".pkl"
        )
        self.data["path"] = pj(test_data_path, self.data["filename"])
        self.update()
        self.load()
        if exists(self.path):
            logger.info("since file already exists, setting test_resumed to True")
            self.data["test_resumed"] = True
        else:
            logger.info("since file doesn't exist, setting test_resumed to False")
            self.data["test_resumed"] = False
            logger.info("since file doesn't exist, setting test_completed to False")
            self.data["test_completed"] = False
            logger.info("since file doesn't exist, setting empty remaining_trials")
            self.data["remaining_trials"] = []
            logger.info("since file doesn't exist, setting current_trial to None")
            self.data["current_trial"] = None
            logger.info("since file doesn't exist, setting empty completed_trials")
            self.data["completed_trials"] = []

        logger.info("after fully initialising, object looks like this: %s" % self.data)
        logger.info("checking that trials exist")
        assert "remaining_trials" in self.data, "Missing remaining_trials"
        assert "current_trial" in self.data, "Missing current_trial"
        assert "completed_trials" in self.data, "Missing completed_trials"
        self.update()


class SimpleProcedure:
    def __init__(self, **kwds):
        """Create a simple procedure.

        A procedure is a special iterator over trials. A "simple" procedure starts at
        the first trial and moves forward one trial at each iteration until there are
        no trials remaining or the procedure is aborted.

        """
        logger.info("initialising a SimpleProcedure object with kwds: %s" % str(kwds))
        logger.info("checking that trials exist")
        assert "remaining_trials" in kwds, "Missing remaining_trials"
        assert "current_trial" in kwds, "Missing current_trial"
        assert "completed_trials" in kwds, "Missing completed_trials"

        logger.info("transferring kwds to procedure")
        self.data = {}
        self.data.update(kwds)

        logger.info("making important kwds attributes")
        self.test_resumed = kwds["test_resumed"]
        self.test_completed = kwds["test_completed"]
        self.remaining_trials = kwds["remaining_trials"]
        self.current_trial = kwds["current_trial"]
        self.completed_trials = kwds["completed_trials"]


        # logger.info("loading and converting trials")
        # self.remaining_trials = [Trial(t) for t in kwds["remaining_trials"]]
        # self.current_trial = kwds["current_trial"]
        # if self.current_trial is not None:
        #     self.current_trial = Trial(self.current_trial)
        # else:
        #     self.current_trial = self.current_trial
        # self.completed_trials = [Trial(t) for t in kwds["completed_trials"]]
    #     self.__dict__.update(kwds)
    #     if "test_aborted" not in kwargs:
    #         self.test_aborted = False
    #     if "test_completed" not in kwargs:
    #         self.test_completed = False
    #
    #     # convert dicts to trials
    #     self.remaining_trials = [Trial(t) for t in remaining_trials]
    #     self.completed_trials = [Trial(t) for t in completed_trials]
    #
    #
    # def skip_current_trial(self):
    #     """Set the current trial to skipped.
    #
    #     """
    #     self.current_trial.skipped = True
    #
    # def skip_block(self):
    #     """Set all trials within the current block to skipped, including the current
    #     trial.
    #
    #     """
    #     for trial in self.remaining_trials:
    #         if trial.block_number == self.current_block_number:
    #             trial.skipped = True
    #
    # def abort(self):
    #     """End test now. This involves placing the current trial back in the
    #     remaining trial list and setting `test_aborted` to True.
    #
    #     """
    #     self.remaining_trials = [copy(self.current_trial)] + self.remaining_trials
    #     self.current_trial = None
    #     self.test_aborted = True
    #
    def __iter__(self):
        """Just returns itself."""
        return self

    def __next__(self):
        """Iterate one trial.

        Iterating involves the following steps:

        1. If test was resumed and not completed, convert the current_trial dict to a
            Trial.
        Move current_trial to completed_trials, if there is one.
        remaining and flagging the procedure as complete if so; (2) stopping the
        iterator if the procedure is aborted or complete; and (3) moving the current
        trial to completed trials.

        """
        if len(self.remaining_trials) == 0:

            logger.info("remaining_trials is empty, test must be completed")
            raise StopIteration

        if self.test_resumed:

            logger.info("test was resumed but not flagged as completed")
            assert isinstance(self.current_trial, dict), "current_trial is not a dict"
            logger.info("converting the pre-existing current trial")
            self.current_trial = Trial(self.current_trial)

        else:

            logger.info("test was neither resumed nor flagged as completed")
            assert self.current_trial is None, "current_trial is not None"

            if len(self.remaining_trials) == 0:

                logger.info("no remaining trials, so flagging as completed")
                self.test_completed = True
                raise StopIteration

                logger.info("popping from remaining_trials")
            self.current_trial = Trial(self.remaining_trials.pop(0))

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
    #
    # @property
    # def any_skipped(self):
    #     """:obj:`bool`: Where any trials skipped?"""
    #     return any(t.skipped for t in self.completed_trials)
    #
    # @property
    # def all_skipped(self):
    #     """:obj:`bool`: Where any trials skipped?"""
    #     return all(t.skipped for t in self.completed_trials)
    #
    # @property
    # def not_skipped_trials(self):
    #     """:obj:`list`: List of trials that were not skipped and not "practice" trials,
    #     if there were any."""
    #     trials = [trial for trial in self.completed_trials if not trial.skipped]
    #     if "block_type" in trials[0]:
    #         trials = [trial for trial in trials if trial.block_type != "practice"]
    #     return trials
    #
    # @property
    # def skipped_trials(self):
    #     """:obj:`list`: List of trials that were skipped.and not "practice" trials,
    #     if there were any."""
    #     trials = [trial for trial in self.completed_trials if trial.skipped]
    #     if "block_type" in trials[0]:
    #         trials = [trial for trial in trials if trial.block_type != "practice"]
    #     return trials
    #
    # @property
    # def current_block_number(self):
    #     """:obj:`int`: Block number of current trial."""
    #     return self.current_trial.block_number
    #
    # def trials_from_block(self, bn):
    #     """Return all completed trials from a given block."""
    #     return [trial for trial in self.completed_trials if trial.block_number == bn]