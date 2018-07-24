"""
=============
Visual memory
=============

:Version: 1.0
:Source: http://github.com/sammosummo/Charlie2/tests/visualmemory.py

Description
===========

This test is designed to measure the capacity of visual short-term memory for colours
using a change-localisation task similar to the one employed by [1]_. On each trial, the
proband sees 5 circles, each with a random colour. All circles are removed, then
reappear, but one has changed colour. The proband must click on/touch the changed
circle. There are 30 trials, but after 5 trials, the test will start evaluating
performance and will quit early if chance performance is detected. There is a 30-second
time limit on each trial and a 240-second time limit on the whole experiment.

Reference
=========

.. [1] Johnson, M. K., McMahon, R. P., Robinson, B. M., Harvey, A. N., Hahn, B.,
  Leonard, C. J., Luck, S. J., & Gold, J. M. (2013). The relationship between working
  memory capacity and broad measures of cognitive ability in healthy adults and people
  with schizophrenia. Neuropsychol, 27(2), 220-229.

"""
__version__ = 1.0


from logging import getLogger
from math import cos, sin, pi
from PyQt5.QtGui import QPixmap
from charlie2.tools.basetestwidget import BaseTestWidget


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):

    def __init__(self, parent=None):

        super(TestWidget, self).__init__(parent)

    def make_trials(self):

        names = ["trial_number", "theta"]
        thetas = [
            0.07287796, 0.41152918, 0.91638001, 0.10786362, 0.44804563,
             0.07869748, 0.32707228, 0.13110916, 0.39891674, 0.13511945,
             0.96472743, 0.49840824, 0.75278005, 0.36421804, 0.90371158,
             0.15003588, 0.82969852, 0.04375173, 0.8420186, 0.49465768,
             0.73329339, 0.27312348, 0.66541802, 0.62325591, 0.39011348,
             0.07071519, 0.22071366, 0.64990979, 0.21862013, 0.22426774
        ]
        return [dict(zip(names, params)) for params in enumerate(thetas)]

    def block(self):

        self.block_deadline = 300 * 1000
        self.display_instructions_with_continue_button(self.instructions[4])

    def trial(self):

        t = self.data.current_trial

        logger.info("commencing study phase of trial")
        self.mouse_visible = False
        self.performing_trial = False
        self.clear_screen(delete=False)

        logger.info("about to display items")
        self.labels = []
        delta = 2 * pi / 4
        for item in range(4):
            theta = t.theta * 2 * pi + delta * item
            x = 150 * sin(theta)
            y = 150 * cos(theta)
            s = "l%i_t%i_i%i.png" % (4, t.trial_number, item)
            label = self.display_image(s, (x, y))
            self.labels.append(label)
        self.sleep(3000)

        [label.hide() for label in self.labels]
        self.sleep(2000)

        s = "l%i_t%i_i%i_r.png" % (4, t.trial_number, 0)
        self.labels[0].setPixmap(QPixmap(self.vis_stim_paths[s]))
        [label.show() for label in self.labels]

        self.make_zones(l.frameGeometry() for l in self.labels)
        self.mouse_visible = True
        self.performing_trial = True

    def mousePressEvent_(self, event):

        ix = [event.pos() in z for z in self.zones]
        t = self.data.current_trial
        if any(ix):
            t.rsp = next(i for i, v in enumerate(ix) if v)
            t.correct = t.rsp == 0
            self.data.current_trial.status = "completed"

    def block_stopping_rule(self):

        trials = self.data.completed_trials
        logger.debug(str(trials))
        if len(trials) > 4:
            correct = [t for t in trials if t["correct"]]
            logger.debug(str(correct))
            logger.debug(str(len(correct) / len(trials)))
            return True if len(correct) / len(trials) <= .25 else False
        else:
            return False

    def summarise(self):

        dic = self.basic_summary()
        dic["k"] = dic["accuracy"] * 4
        return dic
