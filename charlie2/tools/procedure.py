"""Defines procedure class.

"""
from datetime import datetime
from copy import copy
from logging import getLogger
from os.path import exists, join as pj
from pickle import dump, load

import pandas as pd

from .paths import csv_path, summaries_path, test_data_path
from .defaults import default_keywords
from .proband import Proband
from .trial import Trial

logger = getLogger(__name__)

keywords = {
    "proband_id",
    "test_name",
    "language",
    "fullscreen",
    "resume",
    "computer_id",
    "user_id",
    "platform",
}
defaults = {k: v for k, v in default_keywords.items() if k in keywords}


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
        logger.info(f"initialised {type(self)} with {kwds}")
        self.data = kwds.copy()
        self.data["filename"] = (
                self.data["proband_id"] + "_" + self.data["test_name"] + ".pkl"
        )
        self.data["path"] = pj(test_data_path, self.data["filename"])
        self.data["csv"] = pj(csv_path, self.data["filename"]).replace(".pkl", ".csv")
        self.data["summary_path"] = pj(summaries_path, self.data["filename"]).replace(
            ".pkl", "_summary.csv"
        )
        if exists(self.data["path"]):
            logger.info("data belonging to proband with this id already exists")
            old_data = load(open(self.data["path"], "rb"))
            missing_data = {k: v for k, v in old_data.items() if k not in self.data}
            self.data.update(missing_data)
            self.data["last_loaded"] = datetime.now()
            self.data["test_resumed"] = True
            if self.data["test_completed"] is False:
                logger.info("add current_trial back to remaining_trials list")
                trial = copy(self.data["current_trial"])
                trial["resumed_from_here"] = True
                trial["status"] = "pending"
                self.data["remaining_trials"] = [trial] + self.data["remaining_trials"]
                self.data["current_trial"] = None

        else:

            logger.info("data do not exist")
            self.data["created"] = datetime.now()
            self.data["test_resumed"] = False
            self.data["test_completed"] = False
            self.data["remaining_trials"] = []
            self.data["current_trial"] = None
            self.data["completed_trials"] = []

        logger.info("filling missing with defaults (most of the time, should be none)")
        self.data.update({k: v for k, v in defaults.items() if k not in self.data})
        self.update()
        logger.info(f"fully initialised, looks like {self.data}")
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
