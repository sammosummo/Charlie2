import pandas as pd
from .paths import csv_path, pkl_path, pkl_exists, pj
from datetime import datetime
from pickle import dump, load
from getpass import getuser


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
        self.proband_id = proband_id
        self.test_name = test_name
        self.last_loaded = None
        self.created = datetime.now()
        self.current_user_id = getuser()
        self.previous_user_id = None
        self.original_user_id = getuser()
        self.test_done = False
        self.control = None
        self.results = []
        self.log = {}
        s = '%s_%s' % (self.proband_id, self.test_name)
        self.pkl_name = f'{s}.pkl'
        self.pkl_path = pj(pkl_path, self.pkl_name)
        self.csv_name = f'{s}.csv'
        self.csv_path = pj(csv_path, self.csv_name)
        self.pkl = locals()
        self.load()

    def load(self):
        """Load pre-existing data (and update current data) if any exist."""

        if pkl_exists(self.test_name, self.proband_id):

            self.pkl.update(load(open(self.pkl_path, 'rb')))
            self.last_loaded = datetime.now()
            self.created = self.pkl['created']
            self.previous_user_id = self.pkl['current_user_id']
            self.original_user_id = self.pkl['original_user_id']
            self.test_done = self.pkl['test_done']
            self.control = self.pkl['control']
            self.results = self.pkl['results']
            self.to_log('Data object loaded.')

        else:

            self.to_log('Attempted to load data object; did not exist.')

    def save(self):
        """Save the data."""
        dump(self.pkl, open(self.pkl_path, 'wb'))
        self.to_log('Data object saved.')

    def to_csv(self):
        """Write the results to a human-readable csv file."""
        pd.DataFrame(self.results).to_csv(self.csv_path, index=False)
        self.to_log('Results written to CSV file.')

    def to_log(self, s):
        """Write the string to the log."""
        self.log[datetime.now()] = s


