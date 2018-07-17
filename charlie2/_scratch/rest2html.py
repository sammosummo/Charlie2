import docutils.core

text = """
================
Orientation test
================

:Status: complete
:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/

Description
===========

This simple test is designed to be administered first in any battery. On each trial, the
proband sees a red square positioned randomly on the screen. The task is to touch the
square as quickly as possible. It is similar to the mouse practice task from [1]_. There
are 10 trials in total and the test automatically quits after 30 s.

Summary statistics
==================

* `completed`: Did the proband complete the test successfully?
* `time_taken`: Time taken to complete the entire test in ms. If the test was not
  completed but at least one trial was performed, this value is the maximum time +
  the number of remaining trials multiplied by the mean reaction time over the completed
  trials.
* `responses` (int): Total number of responses.

Reference
=========

.. [1] Gur, R.C., Ragland, D., Moberg, P.J., Turner, T.H., Bilker, W.B., Kohler, C.,
  Siegel, S.J., & Gur, R.E. (2001). Computerized neurocognitive scanning: I. Methodology
  and validation in healthy people. Neuropsychopharmacol, 25, 766-776.

"""

html = docutils.core.publish_string(source=text, writer_name="html").decode()
html = html[html.find("<body>") + 6 : html.find("</body>")].strip()
print(html)
