"""Defines custom data structures.

"""
from copy import copy
from logging import getLogger
from os.path import exists, join as pj
import pandas as pd
from .paths import test_data_path, csv_path, summaries_path, tests_list
from.proband import Proband

logger = getLogger(__name__)



