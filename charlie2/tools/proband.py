"""Defines a custom Proband object.

"""
from datetime import datetime
from logging import getLogger
from os import remove
from os.path import exists
from os.path import join as pj
from pickle import dump, load

from .paths import proband_path

logger = getLogger(__name__)
forbidden_ids = {"TEST", ""}


class Proband(object):
    def __init__(self, **kwds) -> None:
        """Proband object.

        These objects contain information about the current proband, such as their ID,
        when they were tested, etc. This information is saved in a special .pkl file
        (really just a pickled python dictionary).

        Kwds:
            proband_id (str): The proband ID. This is the only keyword required at
            initialisation. Others will be inherited in the following order:
                1. Generic defaults.
                2. Previously saved to disk.
                3. Passed upon initialisation.
                4. Automatically determined based on `proband_id`.

        """
        logger.debug(f"initialised {type(self)} with {kwds}")
        assert "proband_id" in kwds, "proband_id must be a keyword argument"

        self.proband_id = kwds["proband_id"]
        self.filename = f"{self.proband_id}.pkl"
        self.path = pj(proband_path, self.filename)
        autos = {
            "proband_id": self.proband_id,
            "filename": self.filename,
            "path": self.path,
        }
        stored = self.load()
        defaults = {
            "proband_id": "TEST",
            "age": 1,
            "sex": "Male",
            "other_ids": set(),
            "notes": "Add notes about the proband here...",
        }
        self.data = {**defaults, **stored, **kwds, **autos}
        self.update()

        logger.debug(f"fully initialised, looks like {self.data}")

    def load(self) -> dict:
        """Load data from disk if any exist."""
        logger.debug("called load()")
        dic = {}
        if exists(self.path):
            logger.debug("data belonging to proband with this id already exists")
            dic.update(load(open(self.path, "rb")))
            dic["last_loaded"] = datetime.now()
        else:
            logger.debug("data belonging to proband with this id not found on disk")
            dic["created"] = datetime.now()
        logger.debug(f"loaded data looks like this: {dic}")
        return dic

    def save(self) -> None:
        """Dump the data. Don't do this if proband ID is TEST."""
        logger.debug("called save()")
        if self.proband_id.upper() not in forbidden_ids:
            self.backup()
            logger.debug("saving the data")
            self.data["last_saved"] = datetime.now()
            dump(self.data, open(self.path, "wb"))
        else:
            logger.debug("not saving the data: forbidden ID")
        self.update()

    def update(self) -> None:
        """Updates the attributes according to the internal dictionary."""
        logger.debug("called update()")
        self.__dict__.update(self.data)

    def delete(self) -> None:
        """Delete the proband from disk."""
        logger.debug("called delete()")
        self.backup()
        if exists(self.path):
            remove(self.path)

    def backup(self) -> None:
        """Make a backup."""
        pass
        # logger.debug("called backup()")
        # if exists(self.data["path"]):
        #     logger.warning("making a backup of previously saved data")
        #     path = self.path.replace("current", "old")
        #     for i in range(8, 0, -1):
        #         path_ = path + f".{i}"
        #         if exists(path_):
        #             move(path_, path + f"{i + 1}")
        #     move(self.path, path + ".1")
