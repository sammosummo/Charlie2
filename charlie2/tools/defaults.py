"""Defines default values of keywords.

"""
from getpass import getuser
from logging import getLogger
from socket import gethostname
from sys import platform


logger = getLogger(__name__)
forbidden_ids = {"TEST", ""}
this_user = getuser()
this_computer = gethostname()

default_keywords = {
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
    "computer_id": this_computer,
    "user_id": this_user,
    "platform": platform,
    "notes": "Add notes about the proband here...",
    "gui": True,
}

_fmw = {
    "batch_name",
    "test_name",
    "test_names",
    "language",
    "fullscreen",
    "resume",
    "autobackup",
    "gui",
}

defaults_for_mainwidow = {k: v for k, v in default_keywords.items() if k in _fmw}