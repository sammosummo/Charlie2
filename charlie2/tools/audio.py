import pygame.mixer as mixer
from .paths import aud_stim_path, pj


def _init_mixer():

    if mixer.get_init() is None:

        mixer.init()


def stop():
    """Stop a sound from playing."""
    if mixer.get_busy():
        mixer.stop()


def play_sound(f):
    """Plays the wav file specified by f."""
    _init_mixer()
    mixer.Sound(f).play()


def play_feedback(corr):
    """Plays audio feedback. corr is a bool where False means incorrect and
    True means correct."""
    _init_mixer()
    f = pj(aud_stim_path, 'common', ['incorrect.wav', 'correct.wav'][corr])
    mixer.Sound(f).play()



