"""Defines the trial class.

"""
from datetime import datetime
from logging import getLogger


logger = getLogger(__name__)


class Trial(dict):

    def __init__(self, *args, **kwds):
        """Create a trial object.

        Trials objects are fancy dictionaries whose items are also attributes. They are
        initialised exactly like dictionaries except that the resulting object must
        contain the attribute `'trial_number'`. Trials typically contain several other
        attributes in addition to those listed below. Trials from the same experiment
        should contain the same attributes.

        """
        super(Trial, self).__init__(*args, **kwds)
        logger.info(f"initialised {type(self)}")

        self.__dict__ = self
        assert "trial_number" in self.__dict__, "must contain trial_number"
        assert isinstance(self.trial_number, int), "trial_number must be an int"

        defaults = {
            "block_number": 0,
            "status": "pending",
            "practice": False,
            "resumed_from_here": False,
            "timestamp": datetime.now(),
        }
        for k, v in defaults.items():
            if k not in self.__dict__:
                self.__dict__[k] = v
        if self.block_number == 0:
            self.__dict__["first_block"] = True
        else:
            self.__dict__["first_block"] = False
        if self.trial_number == 0:
            self.__dict__["first_trial_in_block"] = True
        else:
            self.__dict__["first_trial_in_block"] = False
        if self.first_block and self.first_trial_in_block:
            self.__dict__["first_trial_in_test"] = True
        else:
            self.__dict__["first_trial_in_test"] = False
        logger.info("finished constructing trial object")