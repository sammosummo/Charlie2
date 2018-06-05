import pandas as pd
from .paths import csv_path, h5_path,pkl_path, pkl_exists, pj
from datetime import datetime
from pickle import dump, load
from getpass import getuser


class Data:

    def __init__(self, proband_id, test_name):
        """Data class.

        Data objects contain all the necessary details to run a given proband
        in a given test and save the data. It allows any test to be resumed if
        prematurely aborted and prevents a proband for completing the same
        test twice.

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

    def save(self):
        """Save the data."""
        dump(self.pkl, open(self.pkl_path, 'wb'))

    def to_csv(self):
        """Write the results to a human-readable csv file."""
        pd.DataFrame(self.results).to_csv(self.csv_path, index=False)

    def to_h5(self):
        """Write the results to one big hdf5 file."""
        s = '%s_%s' % (self.proband_id, self.test_name)
        pd.DataFrame(self.results).to_hdf(pj(h5_path, 'local.h5'), s)


