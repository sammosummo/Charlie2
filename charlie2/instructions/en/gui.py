from charlie2 import __version__, __license__, __copyright__, __email__

instr = [
    f"""Charlie v{__version__}
{__copyright__}
Distributed under {__license__} license
For assistance, please contact {__email__}
""",
    'Proband',
    'Enter ID:*',
    '* Using "TEST" (upper case, no quotation marks) as the\nproband ID will result in no data being saved',
    'Options',
    'Run tests in fullscreen',
    'Resume a test or batch',
    'Backup on exit [not yet implemented]',
    'Test (single)',
    'Select test:',
    'Run single test',
    'Tests (batch)',
    'Select batch file:',
    'Run tests in batch mode',
    'Warning',
    """A proband with ID %s has some data from this test already.
A proband cannot complete the same test twice. It is
possible that either you or someone else entered the
proband ID incorrectly. If so, please make a note of this
now. The current test will close.
    
This behavior could be expected if you are resuming a test
or batch of tests. If so, please rerun using the command-
line argument "-r y" or check the "Resume a test or batch"
box in the GUI.""",
    "Ok",
]