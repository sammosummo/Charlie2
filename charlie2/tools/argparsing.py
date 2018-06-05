from argparse import ArgumentParser


description = 'Charlie2: A neurocognitive test battery.'


def get_parser():
    """Parse command-line arguments."""
    parser = ArgumentParser(description=description)
    parser.add_argument(
        '-p',
        '--proband_id',
        default='TEST',
        help='Proband ID. If omitted, no data will be saved.'
    )
    parser.add_argument(
        '-t',
        '--test_names',
        default='',
        help='Name or names of test to run.'
    )
    parser.add_argument(
        '-b',
        '--batch_name',
        default='',
        help='Name of batch file (e.g., `safs1`). Overrules `--test_names`.'
    )
    parser.add_argument(
        '-l',
        '--language',
        default='en',
        help='Two-letter code for language (e.g., `en`).'
    )
    return parser
