from charlie2 import __version__, __license__, __copyright__, __email__

instr = [
    f"""Charlie v{__version__}
{__copyright__}
Distributed under {__license__} license
For assistance, please contact {__email__}
""",
    'Tests',
    'Proband',
    'Select or enter new ID:',
    """NOTE: Using "TEST" (upper case, no quotation marks) as
the proband ID will result in no data being saved. In this
case, the fields below are irrelevant.""",
    'Options',
    'Run tests in fullscreen',
    'Resume a test or batch',
    'Backup on exit [not yet implemented]',
    'Test (single)',
    'Select test:',
    'Run single test',
    'Tests (batch)',
    'Select batch file:*',
    'Run tests in batch mode',
    'Docs',
    'Select a test:',
    """* Using "Cmd+Q/Alt+F4" while in batch mode will skip to
the next test, not exit completely.""",
    'Backup',
    "Additional information",
    """The information below is optional but recommended to
ensure the proband's cognitive data can be matched to their
other data.""",
    "Age (years):",
    "Sex:",
    "Other IDs (e.g., genetic):",
]
