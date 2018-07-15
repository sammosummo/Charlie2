def basic_summary(self, trials=None, adjust_time_taken=False):
    """Returns an basic set of summary statistics.

    Args:
        trials (:obj:`list` of :obj:`Trial`, optional): List of trials to analyse.
            By default this is `self.completed_trials`, but doesn't have to be, for
            example if condition-specific summaries are required.
        adjust_time_taken (:obj:`bool`, optional): Apply adjustment to time_taken.

    Returns:
        dic (dict): dictionary of results.

    """
    if self.procedure.all_skipped:
        return {'completed': False}

    # get all completed trials
    if trials is None:
        trials = self.procedure.completed_trials

    skipped = [t for t in trials if t.skipped]
    any_skipped = len(skipped) > 0

    if all('block_type' in trial for trial in trials):
        trials = [t for t in trials if t.block_type != "practice"]

    # count responses and skips
    not_skipped = [t for t in trials if not t.skipped]
    dic = {
        'completed': True,
        'responses': len(not_skipped),
        'any_skipped': any_skipped,
    }

    # this is the easiest case
    if not any_skipped and not self.data.test_resumed:
        dic['time_taken'] = trials[-1].time_elapsed

    # more complicated
    elif not any_skipped and self.data.test_resumed:
        idx = [trials.index(t) - 1 for t in trials if 'resumed_from_here' in t]
        res = sum([trials[i].time_elapsed for i in idx])
        dic['time_taken'] = trials[-1].time_elapsed + res

    # not meaningful
    elif any_skipped and not adjust_time_taken:
        pass

    # adjustment
    elif any_skipped and adjust_time_taken:
        meanrt = sum(t.rt for t in not_skipped) / len(not_skipped)
        dic['time_taken'] = int(self.block_max_time * 1000 + meanrt * len(skipped))

    else:
        raise AssertionError('should not be possible!')

    # accuracy
    if 'correct' in trials[0]:
        dic['correct'] = len([t for t in not_skipped if t.correct])
        dic['accuracy'] = dic['correct'] / dic['responses']

    return dic






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
#         or test, those data are used to update the current data and procedure
# instances.
#         This allows any test to be resumed if prematurely aborted, and prevents
# proband
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
#         Proband objects are similar to Data objects except that there is one per
# proband
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
# def clear_screen(self, delete=False):
    #     """Hide widgets.
    #
    #     Hides and optionally deletes all children of this widget.
    #
    #     Args:
    #         delete (:obj:`bool`, optional): Delete the widgets as well.
    #
    #     """
    #     # for widgets  organized in a layout
    #     if self.layout() is not None:
    #         while self.layout().count():
    #             item = self.layout().takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.hide()
    #                 if delete:
    #                     widget.deleteLater()
    #             else:
    #                 self.clearLayout(item.layout())
    #     # for widgets not organized
    #     for widget in self.children():
    #         if hasattr(widget, 'hide'):
    #             widget.hide()
    #         if delete:
    #             widget.deleteLater()

#
#
# self.performing_trial = False
#
# self._stop_trial_deadline()
# self._trial_time.restart()
#
# summary['resumed'] = self.data.test_resumed
#
#
#
#
#
# self._test_time.start()
#         self._block_time.start()
#         self._trial_time.start()
#         self._block_timeout_timer = QTimer()
#         self._trial_timeout_timer = QTimer()
#
# # add a flag to the procedure to say that we resumed the test
#         if self.data.test_resumed and not self.data.test_completed:
#             self.data.proc.remaining_trials[0].resumed_from_here = True
