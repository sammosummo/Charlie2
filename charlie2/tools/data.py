"""Defines the custom data class which is responsible for loading and saving the
proband-generated data.

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


class ProbandData:
    def __init__(self, **kwargs):
        """Create a proband data object.

        These objects contain information about the current proband, such as their ID,
        when they were tested, etc. This information is saved in a special .pkl file
        (really just a pickled python dictionary). When the object is initialised, it
        will try to load any pre-existing information about the proband, which can be
        overwritten if necessary.

        Kwargs:
            proband_id (:obj"`str`, optional): Proband's ID. Defaults to `"TEST"`. If
                the default value is used, the data will not be saved anywhere.

        """
        logger.info("initialising a ProbandData object with kwargs: %s" % str(kwargs))
        self.data = {}
        self.data.update(kwargs)
        if "proband_id" not in kwargs:
            self.data["proband_id"] = "TEST"
        self.data["current_computer_id"] = this_computer
        self.data["current_user_id"] = this_user
        self.data["filename"] = self.data["proband_id"] + ".pkl"
        self.data["path"] = pj(proband_path, self.data["filename"])
        self.__dict__.update(self.data)
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
        self.__dict__.update(self.data)

    def save(self):
        """Dump the data. Don't do this if proband ID is TEST."""
        logger.info("called save()")
        if self.proband_id.upper() not in forbidden_ids:
            logger.info("saving the data")
            self.data["saved"] = datetime.now()
            dump(self.data, open(self.path, "wb"))
            self.__dict__.update(self.data)
        else:
            logger.info("not saving the data")


class TestData(ProbandData):
    def __init__(self, **kwargs):
        """Create a test data object.

        Similar to ProbandData but for individual tests. Contains all the necessary
        information for a proband to perform/resume a test, and to calculate summary
        statistics. This information is saved in a special .pkl file (really just a
        pickled python dictionary). When the object is initialised, it will try to load
        any pre-existing information about the proband, which can be overwritten if
        necessary.

        Kwargs:
            proband_id (:obj"`str`, optional): Proband's ID. Defaults to `"TEST"`. If
                the default value is used, the data will not be saved anywhere.
            test_name (str): Name of the test. This must match the name of the .py file
                in the test subdirectory (without the .py extenstion).

        """
        logger.info("initialising a TestData object with kwargs: %s" % str(kwargs))
        assert "test_name" in kwargs, "Missing test_name keyword argument"

        logger.info("initialising a corresponding ProbandData object")
        ProbandData(**kwargs).save()

        self.data = {}
        self.data.update(kwargs)
        if "proband_id" not in kwargs:
            self.data["proband_id"] = "TEST"
        self.data["current_computer_id"] = this_computer
        self.data["current_user_id"] = this_user
        self.data["filename"] = \
            self.data["proband_id"] + "_" + self.data["test_name"] + ".pkl"
        self.data["path"] = pj(test_data_path, self.data["filename"])
        self.__dict__.update(self.data)
        self.load()
        logger.info("after fully initialising, object looks like this: %s" % self.data)

        if exists(self.path):
            logger.info("since file already exists, setting test_resumed to True")
            self.data["test_resumed"] = True

        else:

            logger.info("since file doesn't exists, setting test_resumed to False")
            self.data["test_resumed"] = False
            logger.info("since file doesn't exists, setting test_completed to False")
            self.data["test_completed"] = False

        self.__dict__.update(self.data)



        #         s = "%s_%s" % (self.proband_id, self.test_name)
        #         self.pkl_name = f"{s}.pkl"
        #         self.csv_name = f"{s}.csv"
        #         self.pkl_path = pj(pkl_path, self.pkl_name)
        #         self.csv_path = pj(csv_path, self.csv_name)



# from .paths import csv_path, pkl_path, pj
# from copy import copy
# from datetime import datetime
# from pickle import dump, load
#
# from os.path import basename, exists
#
#
#
#
#
# class Proband:
#     def __init__(self, **kwargs):
#         """Create a Probanddata object.
#
#         Data objects contain details about given proband and test. Upon instantiation,
#         a procedure is also instantiated. If any data have been saved for this proband
#         or test, those data are used to update the current data and procedure
# instances.
#         This allows any test to be resumed if prematurely aborted, and prevents
# proband
#         ID from being used for the same test twice.
#
#
# # class Data:
# #     def __init__(self, **kwargs):
# #         """Create a data object.
#
#         Data objects contain details about given proband and test. Upon instantiation,
#         a procedure is also instantiated. If any data have been saved for this proband
#         or test, those data are used to update the current data and procedure instances.
#         This allows any test to be resumed if prematurely aborted, and prevents proband
#         ID from being used for the same test twice.
#
#         Kwargs:
#             proband_id (str): Proband's ID.
#             test_name (str): Name of the test.
#             remaining_trials (list): List of trials to run in test.
#             procedure (obj): A kind of procedure object.
#             **kwargs: Additional keyword arguments to be stored alongside the data.
#
#         Returns:
#             data: An instance of Data.
#
#         """
#         # check if required kwargs passed
#         required = ('proband_id', 'test_name', 'remaining_trials', 'procedure')
#         assert all(s in kwargs for s in required), "missing required kwargs"
#
#         # store known variables
#         self.__dict__.update(kwargs)
#         self.current_user_id = getuser()
#         s = "%s_%s" % (self.proband_id, self.test_name)
#         self.pkl_name = f"{s}.pkl"
#         self.csv_name = f"{s}.csv"
#         self.pkl_path = pj(pkl_path, self.pkl_name)
#         self.csv_path = pj(csv_path, self.csv_name)
#
#         # print only if verbose flag is set from the command line or elsewhere
#         self.vprint = print if self.verbose else lambda *a, **k: None
#
#         # create unknown variables ambiguously
#         self.first_created = None
#         self.last_loaded = None
#         self.original_user_id = None
#         self.previous_user_id = None
#         self.log = {}
#         self.summary = {}
#         self.completed_trials = []
#         self.current_trial = None
#         self.test_aborted = None
#         self.test_completed = None
#         self.test_resumed = None
#
#         # attempt to load existing data
#         self.load()
#
#         # instantiate procedure
#         self.vprint("creating procedure with these arguments:")
#         self.vprint("   ", 'remaining_trials:', self.remaining_trials)
#         self.vprint("   ", 'completed_trials:', self.completed_trials)
#         self.vprint("   ", 'current_trial:', self.current_trial)
#         self.proc = self.procedure(
#             self.remaining_trials, self.completed_trials, self.current_trial
#         )
#
#         # remove useless/meaningless attributes
#         for name in ("test_names", "batch_name"):
#             if name in self.__dict__:
#                 del self.__dict__[name]
#
#     @property
#     def safe_vars(self):
#         """:obj:`dict`: Variables to save as a pickle. So that this is done safely,
#         only "primitive" Python objects are included."""
#         # update details from procedure
#         self.remaining_trials = [dict(trial) for trial in self.proc.remaining_trials]
#         self.completed_trials = [dict(trial) for trial in self.proc.completed_trials]
#         if self.proc.current_trial is None:
#             self.current_trial = None
#         else:
#             self.current_trial = dict(self.proc.current_trial)
#         self.test_aborted = self.proc.test_aborted
#         self.test_completed = self.proc.test_completed
#
#         # determine which vars to save
#         prim = (bool, int, float, str, list, tuple, set, dict, type(None))
#         dic = {k: v for k, v in self.__dict__.items() if isinstance(v, prim)}
#
#         # return a copy (to be extra safe)
#         return copy(dic)
#
#     def load(self):
#         """Load pre-existing data (and update current data) if any exist."""
#         self.vprint("looking for", self.pkl_path)
#         if exists(self.pkl_path) and self.proband_id != 'TEST':
#             self.vprint("found a pickle for this test and subject")
#
#             # load previous pkl
#             prev_vars = load(open(self.pkl_path, "rb"))
#
#             # update variables
#             self.__dict__.update(prev_vars)
#             self.last_loaded = datetime.now()
#             self.previous_user_id = copy(self.current_user_id)
#             self.current_user_id = getuser()
#             self.to_log("data loaded.")
#             if self.test_completed and not self.test_resumed:
#                 self.test_resumed = False
#                 self.to_log("test was already completed.")
#             else:
#                 self.test_resumed = True
#             self.vprint("data loaded")
#
#         else:
#
#             self.vprint("no pickle found for this test and subject")
#             # update variables
#             self.first_created = datetime.now()
#             self.original_user_id = getuser()
#             self.test_resumed = False
#             self.to_log("data object created.")
#
#     def save(self):
#         """Save the data."""
#         obj = self.safe_vars
#         print(obj)
#         if self.proband_id != "TEST":
#             self.to_log("data object saved.")
#             dump(obj, open(self.pkl_path, "wb"))
#             self.vprint("saved data to", self.pkl_path)
#             self.to_log('data saved')
#         else:
#             self.vprint("not saving because proband is TEST")
#
#     def to_log(self, s):
#         """Write the string to the log."""
#         self.log[datetime.now()] = s
#
#
# def load_data_from_file(src):
#     """Return a data object reconstructed from the pickled object at `src`.
#
#     Args:
#         src (str): Path to pickled object.
#
#     Returns:
#         data (Data): Data object.
#
#     """
#     a, b = basename(src).split('_')
#     return Data(proband_id=a, test_name=b, remaining_trials=[], procedure=None)
#
#
# class Proband(Data):
#     def __init__(self, **kwargs):
#         """Create a proband object.
#
#         Proband objects are similar to Data objects except that there is one per proband
#         rather than per proband and test.
#
#         Kwargs:
#             proband_id (str): Proband's ID.
#             proband_age (str): Proband's age.
#             proband_sex (str): Proband's sex.
#             other_ids (set): Other IDs assigned to the proband.
#             **kwargs: Additional keyword arguments to be stored alongside the data.
#
#         Returns:
#             proband: An instance of Proband.
#
#         """
#         # check if required kwargs passed
#         required = ('proband_id', 'proband_age', 'proband_sex', 'other_ids')
#         assert all(s in kwargs for s in required), "missing required kwargs"
#
#         # store known variables
#         self.__dict__.update(kwargs)
#         self.current_user_id = getuser()
#         s = "%s" % self.proband_id
#         self.pkl_name = f"{s}.ppkl"
#         self.csv_name = f"{s}.pcsv"
#         self.pkl_path = pj(pkl_path, self.pkl_name)
#         self.csv_path = pj(csv_path, self.csv_name)
#
#         # print only if verbose flag is set from the command line or elsewhere
#         self.vprint = print if self.verbose else lambda *a, **k: None
#
#         # create unknown variables ambiguously
#         self.first_created = None
#         self.last_loaded = None
#         self.original_user_id = None
#         self.previous_user_id = None
#         self.log = {}
#
#         self.load()
#
#         # remove useless/meaningless attributes
#         for name in ("test_names", "batch_name", "language", "gui", "fullscreen",
#                      "verbose", "resume", "test_name", "test_resumed"):
#             if name in self.__dict__:
#                 del self.__dict__[name]
#
#     @property
#     def safe_vars(self):
#         """:obj:`dict`: Variables to save as a pickle. So that this is done safely,
#         only "primitive" Python objects are included."""
#         # determine which vars to save
#         prim = (bool, int, float, str, list, tuple, set, dict, type(None))
#         dic = {k: v for k, v in self.__dict__.items() if isinstance(v, prim)}
#         # return a copy (to be extra safe)
#         return copy(dic)
#
#     def load(self):
#         """Load pre-existing data (and update current data) if any exist."""
#         self.vprint("looking for", self.pkl_path)
#         if exists(self.pkl_path) and self.proband_id != 'TEST':
#             self.vprint("found a pickle for this test and subject")
#
#             # load previous pkl
#             prev_vars = load(open(self.pkl_path, "rb"))
#             if 'override' in self.__dict__:
#                 if self.override is True:
#                     for name in ('proband_age', 'proband_sex', 'other_ids'):
#                         del prev_vars[name]
#
#             # update variables
#             self.__dict__.update(prev_vars)
#             self.last_loaded = datetime.now()
#             self.previous_user_id = copy(self.current_user_id)
#             self.current_user_id = getuser()
#             self.to_log("data loaded.")
#             self.vprint("data loaded")
#
#         else:
#
#             self.vprint("no pickle found for this test and subject")
#             # update variables
#             self.first_created = datetime.now()
#             self.original_user_id = getuser()
#             self.test_resumed = False
#             self.to_log("data object created.")
