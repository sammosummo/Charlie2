"""Contains default keywords.

"""
from getpass import getuser
from socket import gethostname
from sys import platform


default_kwds = {  # default values for all useful keywords
    "proband_id": "TEST",
    "batch_name": None,
    "test_name": None,
    "test_names": [],
    "language": "en",
    "fullscreen": [True, False][platform == "darwin"],
    "resume": False,
    "autobackup": False,
    "age": 1,
    "sex": "Male",
    "other_ids": set(),
    "computer_id": gethostname(),
    "user_id": getuser(),
    "platform": platform,
    "notes": "Add copious notes about the proband here...",
}

valid_for_probands = {  # keywords that should be stored for a given proband
    "proband_id",
    "age",
    "sex",
    "other_ids",
    "notes",
    "language",
}

valid_for_tests = {  # keywords that should be stored for a given test
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
