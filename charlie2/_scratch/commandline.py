"""Retrieve information from the command line. Args are imported into and become
attributes of the MainWindow instance. These attributes can be overwritten by the
GUIWidget instance if in GUI mode.

"""
import argparse
from argparse import ArgumentParser

from .recipes import str2bool


def get_parser():
    """Parse command-line arguments."""
    description = "Charlie2: A neurocognitive test battery."
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-p",
        "--proband_id",
        default="TEST",
        help="Proband ID. If omitted, no data will be saved.",
    )
    parser.add_argument(
        "-t", "--test_names", default="", help="Name or names of test to run."
    )
    parser.add_argument(
        "-b",
        "--batch_name",
        default="",
        help="Name of batch file (e.g., `safs1`). Overrules `--test_names`.",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="en",
        help="Two-letter code for language (e.g., `en`).",
    )
    parser.add_argument(
        "-g",
        "--gui",
        type=str2bool,
        default=False,
        help="Activate the GUI first? (default is no).",
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        type=str2bool,
        default=True,
        help="Run tests in fullscreen? (default is yes).",
    )
    parser.add_argument(
        "-v", "--verbose", type=str2bool, default=True, help="Verbose mode."
    )
    parser.add_argument(
        "-r",
        "--resume",
        type=str2bool,
        default=False,
        help="Resume testing of a proband? (default is no).",
    )
    parser.add_argument("-a", "--proband_age", default="1", help="Age of proband.")
    parser.add_argument("-s", "--proband_sex", default="Male", help="Sex of proband.")
    parser.add_argument("-o", "--other_ids", default="", help="Other IDs.")
    parser.add_argument(
        "-k", "--autobackup", type=str2bool, default=True, help="Enable autobackups."
    )
    parser.add_argument("-n", "--notes", default="", help="Notes about proband.")
    return parser
