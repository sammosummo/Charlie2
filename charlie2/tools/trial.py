"""Defines the trial class.

"""


class Trial(dict):
    def __init__(self, *args, **kwargs):
        """Create a trial.

        Trials are essentially fancy dictionaries whose items are also attributes.
        They are initialised exactly like dictionaries except that the resulting object
        must contain the attribute `'trial_number'`. Trials typically contain several
        other attributes in addition to those listed below. Trials from the same
        experiment should contain the same attributes if they have the same values of
        `'completed'` and `'aborted'`.

        Documentation for dictionaries:
            https://docs.python.org/3/library/stdtypes.html#dict

        Attributes:
            trial_number (int): Trial number, starting from `0`.
            first_block (bool): Automatically generated.
            first_trial_in_block (bool): Automatically generated.
            first_trial_in_test (bool): Automatically generated.
            block_number (:obj:`int`, optional): Defaults to `0`.
            completed (:obj:`bool`, optional): Defaults to `False`.
            skipped (:obj:`bool`, optional): Defaults to `False`.

        """
        super(Trial, self).__init__(*args, **kwargs)
        self.__dict__ = self
        assert "trial_number" in self.__dict__, "must contain 'trial_number'"
        assert isinstance(self.trial_number, int), "'trial_number' must be an int"
        defaults = {
            "block_number": 0,
            "completed": False,
            "skipped": False,
        }
        for k, v in defaults.items():
            if k not in self.__dict__:
                self.__dict__[k] = v
        if self.block_number == 0:
            self.__dict__['first_block'] = True
        else:
            self.__dict__['first_block'] = False
        if self.trial_number == 0:
            self.__dict__['first_trial_in_block'] = True
        else:
            self.__dict__['first_trial_in_block'] = False
        if self.first_block and self.first_trial_in_block:
            self.__dict__['first_trial_in_test'] = True
        else:
            self.__dict__['first_trial_in_test'] = False
