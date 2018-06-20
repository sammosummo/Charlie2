"""Defines the custom data class which is responsible for loading and saving the
proband-generated data.

"""
from .paths import csv_path, pkl_path, pj
from copy import copy
from datetime import datetime
from pickle import dump, load
from getpass import getuser
from os.path import exists


class Data:
    def __init__(self, **kwargs):
        """Create a data object.

        Data objects contain details about given proband and test. Upon instantiation,
        a procedure is also instantiated. If any data have been saved for this proband
        or test, those data are used to update the current data and procedure instances.
        This allows any test to be resumed if prematurely aborted, and prevents proband
        ID from being used for the same test twice.

        Kwargs:
            proband_id (str): Proband's ID.
            test_name (str): Name of the test.
            remaining_trials (list): List of trials to run in test.
            procedure (obj): A kind of procedure object.
            **kwargs: Additional keyword arguments to be stored alongside the data.

        Returns:
            Data: An instance of Data.

        """
        # check if required kwargs passed
        required = ('proband_id', 'test_name', 'remaining_trials', 'procedure')
        assert all(s in kwargs for s in required), "missing required kwargs"

        # store known variables
        self.__dict__.update(kwargs)
        self.current_user_id = getuser()
        s = "%s_%s" % (self.proband_id, self.test_name)
        self.pkl_name = f"{s}.pkl"
        self.csv_name = f"{s}.csv"
        self.pkl_path = pj(pkl_path, self.pkl_name)
        self.csv_path = pj(csv_path, self.csv_name)

        # print only if verbose flag is set from the command line or elsewhere
        self.vprint = print if self.verbose else lambda *a, **k: None

        # create unknown variables ambiguously
        self.first_created = None
        self.last_loaded = None
        self.original_user_id = None
        self.previous_user_id = None
        self.log = {}
        self.summary = {}
        self.completed_trials = []
        self.current_trial = None
        self.test_aborted = None
        self.test_completed = None
        self.test_resumed = None

        # attempt to load existing data
        self.load()

        # instantiate procedure
        self.vprint("creating procedure with these arguments:")
        self.vprint("   ", 'remaining_trials:', self.remaining_trials)
        self.vprint("   ", 'completed_trials:', self.completed_trials)
        self.vprint("   ", 'current_trial:', self.current_trial)
        self.proc = self.procedure(
            self.remaining_trials, self.completed_trials, self.current_trial
        )

        # remove useless/meaningless attributes
        for name in ("test_names", "batch_name"):
            if name in self.__dict__:
                del self.__dict__[name]

    @property
    def safe_vars(self):
        """:obj:`dict`: Variables to save as a pickle. So that this is done safely,
        only "primitive" Python objects are included."""
        # update details from procedure
        self.remaining_trials = [dict(trial) for trial in self.proc.remaining_trials]
        self.completed_trials = [dict(trial) for trial in self.proc.completed_trials]
        if self.proc.current_trial is None:
            self.current_trial = None
        else:
            self.current_trial = dict(self.proc.current_trial)
        self.test_aborted = self.proc.test_aborted
        self.test_completed = self.proc.test_completed

        # determine which vars to save
        prim = (bool, int, float, str, list, tuple, set, dict, type(None))
        dic = {k: v for k, v in self.__dict__.items() if isinstance(v, prim)}

        # return a copy (to be extra safe)
        return copy(dic)

    def load(self):
        """Load pre-existing data (and update current data) if any exist."""
        self.vprint("looking for", self.pkl_path)
        if exists(self.pkl_path) and self.proband_id != 'TEST':
            self.vprint("found a pickle for this test and subject")

            # load previous pkl
            prev_vars = load(open(self.pkl_path, "rb"))

            # update variables
            self.__dict__.update(prev_vars)
            self.last_loaded = datetime.now()
            self.previous_user_id = copy(self.current_user_id)
            self.current_user_id = getuser()
            self.to_log("data loaded.")
            if self.test_completed and not self.test_resumed:
                self.test_resumed = False
                self.to_log("test was already completed.")
            else:
                self.test_resumed = True
            self.vprint("data loaded")

        else:

            self.vprint("no pickle found for this test and subject")
            # update variables
            self.first_created = datetime.now()
            self.original_user_id = getuser()
            self.test_resumed = False
            self.to_log("data object created.")

    def save(self):
        """Save the data."""
        obj = self.safe_vars
        if self.proband_id != "TEST":
            self.to_log("data object saved.")
            dump(obj, open(self.pkl_path, "wb"))
            self.vprint("saved data to", self.pkl_path)
            self.to_log('data saved')
        else:
            self.vprint("not saving because proband is TEST")

    def to_log(self, s):
        """Write the string to the log."""
        self.log[datetime.now()] = s

