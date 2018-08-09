"""Defines a base class for widgets.

"""
from sys import gettrace

from PyQt5.QtWidgets import QWidget


class DebuggingWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Debugging widget.

        Simply adds a `self.debugging` property, which if True indicates that the code
        is running within a debugger. Allows us to skip things to make tests go faster.

        """
        super(DebuggingWidget, self).__init__(parent)

    @property
    def debugging(self):
        """Is the code running within a debugger?"""
        return gettrace() is not None
