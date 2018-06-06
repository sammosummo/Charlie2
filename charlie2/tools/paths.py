import charlie2
from pkgutil import iter_modules
from os import listdir as ls
from os.path import dirname, exists, join as pj
from importlib import import_module


_path = dirname(charlie2.__file__)
data_path = pj(_path, 'data')
csv_path = pj(data_path, 'csv')
h5_path = pj(data_path, 'h5')
pkl_path = pj(data_path, 'pkl')
stim_path = pj(_path, 'stimuli')
vis_stim_path = pj(stim_path, 'visual')
aud_stim_path = pj(stim_path, 'audio')
tests_path = pj(_path, 'tests')
tests_list = [name for _, name, _ in iter_modules([tests_path])]
instructions_path = pj(_path, 'instructions')
icon_path = pj(vis_stim_path, 'icon', 'icon.png')
fonts_path = pj(_path, 'fonts')
lists_path = pj(_path, 'lists')


def is_test(s):
    """Returns True if `s` is an existing test."""
    return s in tests_list


def get_test(s):
    """Return the Test class from an experiment."""
    return import_module(f'charlie2.tests.{s}').Test


def get_tests_from_batch(s):
    """Return the names of tests from a batch file."""
    return (t.rstrip() for t in open(pj(lists_path, f'{s}.txt')))


def _get_instructions(s, lang):
    """Return the instructions from test `s` in the given language."""
    return import_module(f'charlie2.instructions.{lang}.{s}').instr


def _get_common_instructions(lang):
    """For instructions common to several tests."""
    return _get_instructions('common', lang)


def get_instructions(s, lang):
    """Return the instructions from test `s` in the given language."""
    lst = _get_common_instructions(lang)
    lst += _get_instructions(s, lang)
    return lst


def _get_vis_stim_paths(s):
    """Return dict containing paths to visual stimuli."""
    p = pj(vis_stim_path, s)
    return {n: pj(p, n) for n in ls(p) if n.endswith('.png')}


def _get_aud_stim_paths(s):
    """Return dict containing paths to visual stimuli."""
    p = pj(vis_stim_path, s)
    return {n: pj(p, n) for n in ls(p) if n.endswith('.png')}


def _get_common_vis_stim_paths():
    """For stimuli common to several tests."""
    return _get_vis_stim_paths('common')


def _get_common_aud_stim_paths():
    """For stimuli common to several tests."""
    return _get_aud_stim_paths('common')


def get_vis_stim_paths(s):
    """Return dict containing paths to visual stimuli."""
    dic = _get_common_vis_stim_paths()
    dic.update(_get_vis_stim_paths(s))
    return dic


def get_aud_stim_paths(s):
    """Return dict containing paths to auditory stimuli."""
    dic = _get_common_aud_stim_paths()
    dic.update(_get_aud_stim_paths(s))
    return dic


def csv_exists(s, p):
    """Returns True if a file for proband `p` exists for test `s`."""
    st = f'{s}_{p}'
    csvs = [f for f in ls(csv_path) if f.endswith('.csv') and f.startswith(st)]
    return len(csvs) > 0


def h5_exists():
    """Returns True if there is currently a local hdf5 database."""
    return exists(pj(h5_path, 'local.h5'))


def pkl_exists(s, p):
    """Returns True if a file for proband `p` exists for test `s`."""
    st = f'{s}_{p}'
    csvs = [f for f in ls(pkl_path) if f.endswith('.pkl') and f.startswith(st)]
    return len(csvs) > 0
