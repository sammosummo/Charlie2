"""Defines a Qt widget containing convenience methods for playing sounds.

"""
from logging import getLogger

from PyQt5.QtMultimedia import QSound

from .debugging import DebuggingWidget
from .paths import get_aud_stim_paths

logger = getLogger(__name__)


class AudioWidget(DebuggingWidget):
    def __init__(self, parent=None) -> None:
        """Visual widget.

        Not called directly. Serves as a base class for BaseTestWidget, providing
        methods for drawing to the GUI.

        """
        super(AudioWidget, self).__init__(parent)
        inherit = (
            "proband_id",
            "test_name",
            "language",
            "fullscreen",
            "computer_id",
            "user_id",
            "platform",
            "resumable",
        )
        self.kwds = {k: v for k, v in self.parent().kwds.items() if k in inherit}
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # stimuli paths
        self.aud_stim_paths = get_aud_stim_paths(self.kwds["test_name"])

        # silence
        self.silence = QSound(self.aud_stim_paths["silence.wav"])

        # 440 pip
        self.pip = QSound(self.aud_stim_paths["440.wav"])

        # feedback
        self.correct = QSound(self.aud_stim_paths["correct.wav"])
        self.incorrect = QSound(self.aud_stim_paths["incorrect.wav"])
        self.feedback_sounds = [self.incorrect, self.correct]

        # other sounds
        self.test_over = QSound(self.aud_stim_paths["test_over.wav"])
        self.new_block = QSound(self.aud_stim_paths["new_block.wav"])

    def play_feeback(self, correct):
        """Play either the correct or incorrect sound."""
        sound = self.feedback_sounds[correct]
        if not sound.isFinished():
            pass
        else:
            sound.play()

    def play_pip(self, sleep):
        """Play a regular pip but optionally sleep while its playing."""
        if not self.pip.isFinished():
            pass
        else:
            self.pip.play()
            if sleep:
                while not self.pip.isFinished():
                    self.sleep(10)
