"""Miscellaneous convenience functions go in here.

"""
import argparse


def str2bool(v):
    """Nice function to convert cmd-line args to bool."""
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        """Handy converter from dict to class with attributes."""
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

