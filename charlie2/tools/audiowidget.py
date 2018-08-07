"""Defines a Qt widget containing convenience methods for playing sounds.

"""
from logging import getLogger

from PyQt5.QtWidgets import QWidget

from .paths import get_aud_stim_paths

logger = getLogger(__name__)


class AudioWidget(QWidget):
    def __init__(self, parent=None) -> None:
        """Visual widget.

        Not called directly. Serves as a base class for BaseTestWidget, providing
        methods for drawing to the GUI.

        """
        super(AudioWidget, self).__init__(parent)
        self.kwds = self.parent().kwds
        print(self.kwds)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # stimuli paths
        self.aud_stim_paths = get_aud_stim_paths(self.kwds["test_name"])
