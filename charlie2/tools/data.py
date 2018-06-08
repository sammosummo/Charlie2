import pandas as pd
from .paths import csv_path, pkl_path, pkl_exists, pj
from copy import copy
from datetime import datetime
from pickle import dump, load
from getpass import getuser
from os import listdir


class Data:

    def __init__(self, proband_id, test_name):
        """Data objects contain all the necessary details to run a given
        proband in a given test and save the data. It allows any test to be
        resumed if prematurely aborted and prevents a proband for completing
        the same test twice.

        Args:
            proband_id (str): Proband's ID.
            test_name (str): Name of the test.

        Returns:
            Data: An instance of Data.

        """
        # store known variables
        self.proband_id = proband_id
        self.test_name = test_name
        self.current_user_id = getuser()
        s = '%s_%s' % (self.proband_id, self.test_name)
        self.pkl_name = f'{s}.pkl'
        self.csv_name = f'{s}.csv'
        self.pkl_path = pj(pkl_path, self.pkl_name)
        self.csv_path = pj(csv_path, self.csv_name)

        # create unknown variables ambiguously
        self.created = None
        self.last_loaded = None
        self.original_user_id = None
        self.previous_user_id = None
        self.test_done = None
        self.first_trial = None
        self.first_block = None
        self.control = None
        self.resumed = None
        self.results = None
        self.log = None
        self.summary = None
        self.language = None

        # create empty iterables for data collection
        self.pkl = copy(vars(self))

        # attempt to load existing data
        self.load()

    def load(self):
        """Load pre-existing data (and update current data) if any exist.

        """

        if pkl_exists(self.test_name, self.proband_id):

            # load previous pkl
            pkl = load(open(self.pkl_path, 'rb'))

            # update ambiguous variables
            self.created = pkl['created']
            self.last_loaded = pkl['last_loaded']
            self.original_user_id = pkl['original_user_id']
            self.previous_user_id = pkl['previous_user_id']
            self.test_done = pkl['test_done']
            self.first_trial = pkl['first_trial']
            self.first_block = pkl['first_block']
            self.control = pkl['control']
            self.resumed = True
            self.results = pkl['results']
            self.log = pkl['log']
            self.summary = pkl['summary']
            self.to_log('Previous data object found; contents loaded.')
            self.pkl.update(copy(vars(self)))

        else:

            # update ambiguous variables
            self.created = datetime.now()
            self.last_loaded = False
            self.original_user_id = getuser()
            self.previous_user_id = None
            self.test_done = False
            self.resumed = False
            self.results = []
            self.log = {}
            self.summary = {}
            self.to_log('Previous data object not found; initialise new.')
            self.pkl.update(copy(vars(self)))

    def save(self):
        """Save the data."""

        if self.proband_id != 'TEST':

            self.pkl.update(copy(vars(self)))
            dump(self.pkl, open(self.pkl_path, 'wb'))
            self.to_log('Data object saved.')

    def to_csv(self):
        """Write the results to a human-readable csv file."""

        if self.proband_id != 'TEST':

            pd.DataFrame(self.results).to_csv(self.csv_path, index=False)
            self.to_log('Results written to CSV file.')

    def to_log(self, s):
        """Write the string to the log."""
        self.log[datetime.now()] = s


def make_df():
    """Return all the local data in a pandas DataFrame."""
    paths = [pj(pkl_path, f) for f in listdir(pkl_path) if f.endswith('.pkl')]
    pkls = [load(open(f, 'rb')) for f in paths]
    return pd.DataFrame(pkls)