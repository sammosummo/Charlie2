"""Defines a custom Procedure object. Add more procedure classes in the future.

"""
from datetime import datetime
from getpass import getuser
from logging import getLogger
from os.path import exists
from os.path import join as pj
from pickle import dump, load
from socket import gethostname
from sys import platform
from typing import Union

import pandas as pd

from .paths import csv_path, summaries_path, test_data_path
from .proband import forbidden_ids
from .trial import Trial

logger = getLogger(__name__)


class SimpleProcedure(object):
    def __init__(self, proband_id: str, test_name: str, **kwds) -> None:
        """SimpleProcedure object.

        These objects contain information about a proband and test. This information is
        saved in a special .pkl file (really just a pickled python dictionary).

        Procedure objects are also iterators. When iterated, these objects move trials
        between two special attributes called `remaining_trials` and `completed_trials`.
        Both are lists of dictionaries, which each dictionary representing a trial. When
        the test is over (e.g., when `remaining_trials` if empty), an exception is
        raised.

        "Simple" procedures are those that start at the first trial and move forward one
        trial at a time until there are no trials remaining. This is in contrast to
        adaptive procedures, where new trials might be generated based on prior
        responses (not yet implemented).

        Args:
            proband_id (str): The proband ID. This is required at initialisation.
            test_name (str): The test name. Also required at initialisation.

        Others keywords will be inherited in the following order:
            1. Generic defaults.
            2. Previously saved to disk.
            3. Passed upon initialisation.
            4. Automatically determined based on `proband_id` and `test_name`.

        """
        logger.debug(f"initialised {type(self)} with {kwds}")

        # create some keywords automatically
        self.proband_id = proband_id
        self.test_name = test_name
        self.filename = f"{self.proband_id}_{self.test_name}.pkl"
        self.path = pj(test_data_path, self.filename)
        self.csv = pj(csv_path, self.filename.replace(".pkl", ".csv"))
        s = self.filename.replace(".pkl", "_summary.csv")
        self.summary_path = pj(summaries_path, s)
        autos = {
            "proband_id": self.proband_id,
            "test_name": self.test_name,
            "filename": self.filename,
            "path": self.path,
            "csv": self.csv,
            "summary_path": self.summary_path,
            "started_timestamp": datetime.now(),
            "finished_timestamp": None,
        }
        defaults = {
            "language": "en",
            "computer_id": gethostname(),
            "user_id": getuser(),
            "platform": platform,
            "test_started": False,
            "test_resumed": False,
            "test_completed": False,
            "remaining_trials": [],
            "completed_trials": [],
            "summary": {},
            "delete_skipped": False,
        }
        stored = self.load()

        # store the keywords
        self.data = {**defaults, **stored, **kwds, **autos}
        self.update()

        logger.debug(f"fully initialised, looks like {self.data}")

    def next(self, current_trial: Union[None, Trial, dict] = None) -> Trial:
        """Iterate one trial.

        Iterating involves checking if the test has been completed, defined by having an
        empty remaining_trials list and a non-empty completed_trials list. If so, an
        exception is raised. Otherwise, it checks if the next trial should be skipped.
        If so, that trial is silently moved to the bottom of the completed_trials list
        and the iterator is recursively iterated again. If not, the trial is returned.

        If the optional `current_trial` is not None, this trial is appended (as a
        vanilla dict) to the `completed_trials` list.

        Args:
            current_trial: The current trial.

        Returns:
            charlie2.tools.trial.Trial: The next trial.

        """
        logger.debug(f"called __next__() with current_trial={current_trial}")
        self.data["test_started"] = True

        if current_trial is not None:

            current_trial["finished_timestamp"] = datetime.now()
            if all([
                self.data["delete_skipped"] is True,
                current_trial["status"] == "skipped",
                len(self.data["completed_trials"]) > 0,
            ]):
                pass
            else:
                self.data["completed_trials"].append(current_trial)

        self.data["test_completed"] = all(
            [
                len(self.data["remaining_trials"]) == 0,
                len(self.data["completed_trials"]) > 0,
            ]
        )
        self.to_csv()

        if self.data["test_completed"]:
            logger.debug("stopping iterations")
            self.data["finished_timestamp"] = datetime.now()
            raise StopIteration

        else:
            logger.debug("attempting to iterate")
            trial = self.data["remaining_trials"].pop(0)
            # trial.update({
            #     "_remaining_trials_in_test": self.data["remaining_trials"]
            # })
            # if "block_number" in trial:
            #     rt = [t for t in self.data["remaining_trials"] if
            #           t["block_number"] == trial["block_number"]]
            #     trial.update({
            #         "_remaining_trials_in_block": rt
            #     })

            next_trial = Trial(trial)
            if next_trial.status == "skipped":
                logger.debug("skipping")
                return self.next(dict(next_trial))
            else:
                logger.debug("returning the current trial")
                return next_trial

    def load(self) -> dict:
        """Load attributes of a previously saved object.

        Returns:
            dict: Previously saved attributes of an object with this `proband_id` and
                `test_name`.
        """
        logger.debug("called load()")
        dic = {}

        if exists(self.path):

            logger.debug("data belonging to proband with this id already exists")
            dic.update(load(open(self.path, "rb")))
            dic["last_loaded"] = datetime.now()

            if dic["test_started"] is True and dic["test_completed"] is False:

                dic["test_resumed"] = True
                dic["remaining_trials"][-1]["resumed_from_here"] = True

        else:

            logger.debug("data not found on disk")
            dic["created"] = datetime.now()

        logger.debug(f"loaded data looks like this: {dic}")
        return dic

    def save(self) -> None:
        """Dump the data. Don't do this if proband ID is TEST."""
        logger.debug("called save()")
        if self.proband_id.upper() not in forbidden_ids:
            self.backup()
            logger.debug(f"saving these data: {self.data}")
            self.data["last_saved"] = datetime.now()
            dump(self.data, open(self.path, "wb"))
        else:
            logger.debug("not saving the data: forbidden ID")
        self.update()

    def update(self) -> None:
        """Updates the attributes according to the internal dictionary."""
        logger.debug("called update()")
        self.__dict__.update(self.data)

    def skip_block(self, b: int, reason: str) -> None:
        """Label all trials with the same block number as the last completed trial as
        skipped.

        Args:
            b (int): Block number.
            reason: Reason for skipping.

        """
        trials = self.data["completed_trials"] + self.data["remaining_trials"]
        if all("block_number" in t for t in trials):
            trials = [t for t in trials if t["block_number"] == b]
            for t in trials:
                t["status"] = "skipped"
                t["reason_skipped"] = reason
        else:
            self.skip_all(reason)

    def skip_all(self, reason: str) -> None:
        """Label all trials as skipped.

        Args:
            reason (str): Reason for skipping
        """
        for t in self.data["remaining_trials"]:
            t["status"] = "skipped"
            t["reason_skipped"] = reason

    def to_csv(self) -> None:
        """Write all trials to a csv."""
        trials = self.data["completed_trials"]
        pd.DataFrame(trials).dropna(axis=1, how="all").to_csv(self.csv, index=False)

    def save_summary(self) -> None:
        """Save the summary as a csv"""
        pd.Series(self.data["summary"]).to_csv(self.data["summary_path"])

    def backup(self) -> None:
        """Make a backup."""
        # TODO: Not implemented yet.
        pass
