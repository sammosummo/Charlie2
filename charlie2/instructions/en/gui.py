from charlie2 import __version__, __license__, __copyright__, __email__

instr = [
    f"""Charlie v{__version__}
{__copyright__}
Distributed under {__license__} license
For assistance, please contact {__email__}
""",
    'Tests',
    'Proband',
    'Select or enter new ID*:',
    """*NOTE: Using "TEST" (upper case, no quotation marks) as
the proband ID will result in no data being saved. In this
case, the fields below are ignored. Case sensitive. Alpha-
numeric characters only.""",
    'Testing options',
    'Run tests in full-screen mode',
    'Allow resumable tests/batches',
    'Enable Auto-backup mode',
    'Test (single)',
    'Select single test:',
    'Run single test',
    'Tests (batch)',
    'Select batch file:*',
    'Run tests in batch mode',
    'Documentation for selected test:',
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
    "More IDs (e.g., family ID):",
    "Add",
    "Remove",
    "Save current selection",
    "Local data",
    "Backed-up data",
    "Status",
    "Backup",
    "Back up data now",
    """Computer name: %s
No. proband .pkls: %i
No. test .pkls: %i
No. conflicts: %i""",
    "Attempting backup (%i/5) ...",
    "Backup succeeded.",
    "Backup failed.",
    "Local data files are up to date.",
    "Local files are out of date.",
    "Notes",
    """Use the box below to add notes about the specific proband
and test. NOTE: This does *NOT* affect the selections in the
Proband and Test tabs.""",
    "Save",
    "Reset",
    """*NOTE: The proband ID must be created in the Probands tab
before it can be used. Using "TEST" (upper case, no quotation
marks) as the proband ID will result in no data being saved.""",
    """Select a proband ID:""",
    """Select a testing language:"""
]
