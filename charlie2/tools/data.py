"""Defines custom data structures.

"""
from copy import copy
from datetime import datetime
from getpass import getuser
from logging import getLogger
from os.path import exists, join as pj
from pickle import load, dump
from socket import gethostname
from sys import platform
import pandas as pd
from .paths import proband_path, test_data_path, csv_path, summaries_path, tests_list


logger = getLogger(__name__)
forbidden_ids = {"TEST", ""}
this_user = getuser()
this_computer = gethostname()
default_kwds = {
    "proband_id": "TEST",
    "batch_name": None,
    "test_name": None,
    "test_names": [],
    "language": "en",
    "fullscreen": [True, False][platform == "darwin"],
    "resume": False,
    "autobackup": True,
    "age": 1,
    "sex": "Male",
    "other_ids": set(),
    "computer_id": this_computer,
    "user_id": this_user,
    "platform": platform,
    "notes": "Add copious notes about the proband here...",
    "gui": True,
}
for_probands = {"proband_id", "age", "sex", "other_ids", "notes", "language"}
for_tests = {
    "proband_id",
    "test_name",
    "language",
    "fullscreen",
    "resume",
    "autobackup",
    "computer_id",
    "user_id",
    "platform",
}
for_mainwindow = {
    "batch_name",
    "test_name",
    "test_names",
    "language",
    "fullscreen",
    "resume",
    "autobackup",
    "gui",
}
defaults_for_mainwidow = {k: v for k, v in default_kwds.items() if k in for_mainwindow}


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
        logger.info("initialising a trial data object")
        assert "trial_number" in self.__dict__, "must contain trial_number"
        assert isinstance(self.trial_number, int), "trial_number must be an int"

        logger.info("adding default attributes")
        defaults = {
            "block_number": 0,
            "status": "pending",
            "practice": False,
            "resumed_from_here": False,
            "timestamp": datetime.now(),
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
        logger.info("finished constructing trial object")


class Proband:
    def __init__(self, **kwds):
        """Create a proband data object.

        These objects contain information about the current proband, such as their ID,
        when they were tested, etc. This information is saved in a special .pkl file
        (really just a pickled python dictionary). When the object is initialised, it
        will try to load any pre-existing information about the proband, which can be
        overwritten if necessary.

        """
        logger.info("initialising a proband data object with kwds: %s" % str(kwds))
        self.data = {k: v for k, v in default_kwds.items() if k in for_probands}
        self.data.update(kwds)
        self.data["filename"] = self.data["proband_id"] + ".pkl"
        self.data["path"] = pj(proband_path, self.data["filename"])
        self.update()
        self.load()
        logger.info("after fully initialising, object looks like this: %s" % self.data)

    def load(self):
        """Load pre-existing data, and update current data, if any exist."""
        logger.info("called load()")
        if exists(self.path):
            logger.info("file exists")
            prev_data = load(open(self.path, "rb"))
            self.data.update(prev_data)
            self.data["last_loaded"] = datetime.now()
        else:
            logger.info("file does not exist")
            self.data["created"] = datetime.now()

        logger.info("current data file updated to %s" % str(self.data))
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


class SimpleProcedure(Proband):
    def __init__(self, **kwds):
        """Create a test data object.

        Contains all the necessary information for a proband to perform/resume a test
        and save the data. Important information is saved in a special .pkl file (really
        just a pickled python dictionary). When the object is initialised, it will try
        to load any pre-existing information about the proband, which can be overwritten
        if necessary.
        
        The object is also an iterator over trials. The procedure is  "simple" in the
        sense that it starts at the first trial and moves forward one trial at each
        iteration until there are no trials remaining.

        """
        logger.info("initialising a TestData object with kwds: %s" % str(kwds))
        self.data = {k: v for k, v in default_kwds.items() if k in for_probands}
        self.data.update(kwds)
        assert self.data["test_name"] in tests_list, "test_name not recognised"

        self.data["filename"] = (
            self.data["proband_id"] + "_" + self.data["test_name"] + ".pkl"
        )
        self.data["path"] = pj(test_data_path, self.data["filename"])
        self.data["csv"] = pj(csv_path, self.data["filename"]).replace(".pkl", ".csv")
        self.data["summary_path"] = pj(summaries_path, self.data["filename"]).replace(
            ".pkl", "_summary.csv"
        )
        self.update()
        self.load()

        if exists(self.path):
            logger.info("since file already exists, setting test_resumed to True")
            self.data["test_resumed"] = True
            if self.data["test_completed"] is False:
                logger.info("add current_trial back to remaining_trials list")
                trial = copy(self.data["current_trial"])
                trial["resumed_from_here"] = True
                trial["status"] = "pending"
                self.data["remaining_trials"] = [trial] + self.data["remaining_trials"]
                self.data["current_trial"] = None

        else:
            self.data["test_resumed"] = False
            self.data["test_completed"] = False
            self.data["remaining_trials"] = []
            self.data["current_trial"] = None
            self.data["completed_trials"] = []

        logger.info("after fully initialising, object looks like this: %s" % self.data)
        # logger.debug("completed:", self.data["completed_trials"])
        # logger.debug("current  :", self.data["current_trial"])
        # try:
        #     logger.debug(
        #         "same     :",
        #         self.data["current_trial"] == self.data["completed_trials"][-1]
        #     )
        # except:
        #     pass
        # logger.debug("remaining:", self.data["remaining_trials"])
        self.update()

    def __iter__(self):
        """Just returns itself."""
        return self

    def __next__(self):
        """Iterate one trial."""
        logger.info("iterating one trial")

        if len(self.data["remaining_trials"]) == 0:
            logger.info("remaining_trials is empty, test must be completed")
            self.data["test_completed"] = True
            logger.info("is there an orphaned current_trial?")
            if self.data["current_trial"] is not None:
                logger.info("yes, appending to completed_trials")
                self._append_current_trial()
            self.update()
            raise StopIteration

        if self.data["current_trial"] is None:
            logger.info("no current_trial, so popping new one from remaining_trials")
            self.data["current_trial"] = Trial(self.data["remaining_trials"].pop(0))

        else:
            logger.info("there is a current_trial; what is it?")
            logger.info("current_trial is a %s" % str(type(self.data["current_trial"])))

            if isinstance(self.data["current_trial"], Trial):
                logger.info("must have been created in this session, so appending")
                self._append_current_trial()
                logger.info("and popping new one from remaining_trials")
                self.data["current_trial"] = Trial(self.data["remaining_trials"].pop(0))

            elif isinstance(self.data["current_trial"], dict):
                logger.info("must have been loaded from file, so using it")
                self.data["current_trial"] = Trial(self.data["current_trial"])

        self.update()

        logger.info("current_trial looks like %s" % str(self.data["current_trial"]))
        logger.info("should this trial be skipped?")

        if self.data["current_trial"].status == "skipped":
            logger.info("yes, so recursively iterating")
            return self.__next__()
        else:
            logger.info("no, so returning current_trial")
            return self.data["current_trial"]

    def _append_current_trial(self):
        """Append current_trial to completed_trials, if there is indeed a current_trial
        and it is not already at the bottom of completed_trials.

        """
        logger.info("attempting to append to current_trial to completed_trials")
        ct = self.data["current_trial"]
        # if ct.status != "skipped":
        #     logger.info("setting status of current_trial to completed")
        #     ct.status = "completed"
        # else:
        #     logger.info("preserving status of current_trial as skipped")
        if len(self.data["completed_trials"]) > 0:
            if dict(ct) == self.data["completed_trials"][-1]:
                logger.info("current_trial is last item in completed_trials already")
                return
        logger.info("current_trial is not on completed_trials, so appending")
        self.data["completed_trials"].append(vars(ct))

    def save_completed_trials_as_csv(self):
        """Output the list of dicts as a csv."""
        df = pd.DataFrame(self.data["completed_trials"])
        try:
            df.set_index("trial_number", inplace=True)
        except KeyError:
            logger.warning("No trial_number in data frame, no trials yet?")
        df.dropna(axis=1, how="all", inplace=True)
        df.to_csv(self.data["csv"])
        self.update()

    def save_summary(self):
        """Save the summary as a csv"""
        pd.Series(self.data["summary"]).to_csv(self.data["summary_path"])
        self.update()

    def skip_current_trial(self, reason):
        """Set the current trial to skipped."""
        t = self.data["current_trial"]
        t.status = "skipped"
        t.reason_skipped = reason

    def skip_current_block(self, reason):
        """Set all trials in remaining_trials in the current block, including
        current_trial, to skipped.

        """
        logger.debug("current_trial type: %s" % str(type(self.data["current_trial"])))
        b = self.data["current_trial"].block_number
        logger.debug("current block number: %s" % str(b))
        self.skip_current_trial(reason)
        for i, t in enumerate(self.data["remaining_trials"]):
            logger.debug("trial %s" % str(t))
            if "block_number" in t:
                if t["block_number"] == b:
                    self.data["remaining_trials"][i]["status"] = "skipped"
                    self.data["remaining_trials"][i]["reason_skipped"] = reason
            else:
                self.data["remaining_trials"][i]["status"] = "skipped"
                self.data["remaining_trials"][i]["reason_skipped"] = reason
            logger.debug("trial %s" % str(t))
