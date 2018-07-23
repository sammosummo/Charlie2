"""Contains paths to all files in the battery.

"""
from logging import getLogger
from pkgutil import iter_modules
from os import listdir as ls
from os.path import dirname, exists, join as pj
from importlib import import_module
from copy import copy
import charlie2
from docutils.core import publish_string


logger = getLogger(__name__)

_path = dirname(charlie2.__file__)

data_path = pj(_path, "data")

meta_data_path = pj(data_path, "meta")
last_backed_up = pj(meta_data_path, "last_backed_up.pkl")
credentials_path = pj(meta_data_path, "credentials.json")
token_path = pj(meta_data_path, "token.json")
durations_path = pj(meta_data_path, "durations.csv")

current_data_path = pj(data_path, "current")
proband_path = pj(current_data_path, "probands")
test_data_path = pj(current_data_path, "tests")
csv_path = pj(current_data_path, "csv")
summaries_path = pj(current_data_path, "summaries")

previous_data_path = pj(data_path, "data", "old")
prev_proband_path = pj(previous_data_path, "probands")
prev_test_data_path = pj(previous_data_path, "tests")
prev_csv_path = pj(previous_data_path, "csv")
prev_summaries_path = pj(previous_data_path, "summaries")

stim_path = pj(_path, "stimuli")
vis_stim_path = pj(stim_path, "visual")
aud_stim_path = pj(stim_path, "audio")

tests_path = pj(_path, "tests")
tests_list = [name for _, name, _ in iter_modules([tests_path])]

instructions_path = pj(_path, "instructions")

batch_path = pj(_path, "batch")
batches_list = [b for b in ls(batch_path) if b.endswith(".txt")]

icon_path = pj(vis_stim_path, "icon", "icon.png")
logo_path = pj(_path, "logo", "charlie.png")


def proband_pickles():
    """Returns a sorted list of probands IDs determined by contents of the proband data
    directory.

    """
    return sorted(p.replace(".pkl", "") for p in ls(proband_path) if p.endswith(".pkl"))


def is_test(s):
    """Returns True if `s` is an existing test in the tests sub-package."""
    return s in tests_list


def get_test(s):
    """Returns the test widget from experiment `s`."""
    return import_module(f"charlie2.tests.{s}").TestWidget


def get_tests_from_batch(s):
    """Returns the names of tests from a batch file."""
    return [t.rstrip() for t in open(pj(batch_path, f"{s}"))]


def _get_instructions(s, lang):
    """Returns the instructions from test `s` in the given language."""
    return copy(import_module(f"charlie2.instructions.{lang}.{s}").instr)


def _get_common_instructions(lang):
    """Returns instructions common to several tests in the given language."""
    return _get_instructions("common", lang)


def get_instructions(s, lang):
    """Return instructions from test `s` in the given language."""
    logger.info("getting instructions for %s in language %s" % (s, lang))
    lst = _get_common_instructions(lang)
    lst += _get_instructions(s, lang)
    return lst


def _get_vis_stim_paths(s):
    """Returns a dictionary containing whose keys are the file names of the values are
     absolute paths to visual stimuli for test `s`."""
    p = pj(vis_stim_path, s)
    try:
        return {n: pj(p, n) for n in ls(p) if n.endswith(".png")}
    except FileNotFoundError:
        return {}


def _get_aud_stim_paths(s):
    """Returns a dictionary containing whose keys are the file names of the values are
     absolute paths to auditory stimuli for test `s`."""
    p = pj(aud_stim_path, s)
    try:
        return {n: pj(p, n) for n in ls(p) if n.endswith(".wav")}
    except FileNotFoundError:
        return {}


def _get_common_vis_stim_paths():
    """For stimuli common to several tests."""
    return _get_vis_stim_paths("common")


def _get_common_aud_stim_paths():
    """For stimuli common to several tests."""
    return _get_aud_stim_paths("common")


def get_vis_stim_paths(s):
    """Returns a dictionary containing whose keys are the file names of the values are
     absolute paths to visual stimuli for test `s`."""
    dic = _get_common_vis_stim_paths()
    dic.update(_get_vis_stim_paths(s))
    return dic


def get_aud_stim_paths(s):
    """Returns a dictionary containing whose keys are the file names of the values are
     absolute paths to visual stimuli for test `s`."""
    dic = _get_common_aud_stim_paths()
    dic.update(_get_aud_stim_paths(s))
    return dic


def get_error_messages(lang, name):
    """Returns an error message."""
    return import_module(f"charlie2.instructions.{lang}.errors").__dict__[name]


def get_docstring_html(s):
    """Returns the docstring of a given test, converted from markdown into html."""
    d = import_module(f"charlie2.tests.{s}").__doc__
    html = publish_string(source=d, writer_name="html").decode()
    html = html[html.find("<body>") + 6 : html.find("</body>")].strip()
    return html
