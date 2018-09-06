********
Charlie2
********

:Version: 2.1
:Author: Samuel R. Mathias
:Contact: samuel.mathias@yale.edu
:Github: http://github.com/sammosummo/Charlie2/
:License: MIT

Introduction
============

Charlie2 is a free, open-source, cross-platform neurocognitive test battery written in
Python, with a focus on extendability. It will be used to collect data for one of our
lab projects, but may be used freely by others.

What does it do?
================

Like its predecessor, Charlie2 runs neurocognitive tests. There are currently 9 tests in
the battery, taking ~30 minutes to complete per proband. Each test has a docstring with
citations; have a look in the `charlie2/tests` folder to see what is available.

Notable features
================

* Since Charlie2 is written in Python, it is cross-platform. I have had success running
  it on various platforms, from tablets running Windows 10 to Raspberry Pis.

* Charlie2 works especially well on touchscreen devices.

* Charlie2 has a GUI which allows the user to store/view proband metadata (e.g., their
  age, sex, and miscellaneous notes made before or after testing), run tests
  individually or in pre-defined batches, and back up data to a remote storage server
  such as Google Drive.

* Modifying or adding new tests to Charlie2 is quick, easy and Pythonic.

* Data are recorded after each trial. This means that you have access to trial-specific
  data rather than just the summary data. It also means that the tests are resumable;
  that is, the progress of each proband is retained. This prevents a proband from
  performing a test twice, and allows them to pick up where they left off, if a test
  gets interrupted.

* Summary statistics are automatically computed after a proband completes a test. All of
  the data (summary and trial-specific) are stored within various formats, including
  human-readable csv files and Python pickles.

What's changed
==============

Charlie2 has an entirely new code base. Below are the most significant changes.

* Charlie2 is written in/for Python 3.6 or greater. It does not work with Python 2, and
  probably won't work with earlier versions of Python 3.

* Rather than relying on command-line arguments, Charlie2 is GUI-based.

* Most of the heavy lifting is done by PyQt5, not pygame, which is no longer a
  dependency.

* Questionnaires have been completely removed.

What (still) doesn't work
=========================

* Charlie2 is not stand-alone.

* Charlie2 is **not** currently a regular Python package, so isn't installable via
  `pip`. This probably won't ever happen.

Installation and usage
======================

Charlie is simply a collection of Python scripts. All functionality is accessed from a
PyQt5 application which is launched via `main.py`. If this is not enough information for
you, I recommend performing the following steps:

1. Download and install Miniconda for your platform from here: https://repo.continuum.io/miniconda/

2. Create a new conda environment called `Charlie2` and `activate` it.

3. Run these commands:
   ::
      conda update conda
      conda install pip pyqt pandas
      pip install google-api-python-client oauth2client

4. Download Charlie2: https://github.com/sammosummo/Charlie2/archive/master.zip

5. `cd` to the directory you saved Charlie2 and run `python main.py`.

Change history
==============

2.1: Fixed some bugs which caused crashes during test timeouts.