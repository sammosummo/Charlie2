from importlib import import_module


def get_vwm_stimuli(lang):
    f = f"charlie2.instructions.{lang}.verbalworkingmemory"
    return import_module(f).vwm_sequences
