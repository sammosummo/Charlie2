"""Defines the proband class.

"""
from datetime import datetime
from logging import getLogger
from os import remove
from os.path import exists, join as pj
from pickle import load, dump
from .defaults import default_keywords, forbidden_ids
from.paths import proband_path


logger = getLogger(__name__)
keywords = {"proband_id", "age", "sex", "other_ids", "notes"}
defaults = {k: v for k, v in default_keywords.items() if k in keywords}


class Proband(object):

    def __init__(self, **kwds):
        """Create a proband object.

        These objects contain information about the current proband, such as their ID,
        when they were tested, etc. This information is saved in a special .pkl file
        (really just a pickled python dictionary). When the object is initialised, it
        will try to load any pre-existing information about the proband, which can be
        overwritten if necessary.

        """
        logger.info(f"initialised {type(self)} with {kwds}")
        self.data = kwds.copy()
        self.data["filename"] = self.data["proband_id"] + ".pkl"
        self.data["path"] = pj(proband_path, self.data["filename"])
        if exists(self.data["path"]):
            logger.info("data belonging to proband with this id already exists")
            old_data = load(open(self.data["path"], "rb"))
            missing_data = {k: v for k, v in old_data.items() if k not in self.data}
            self.data.update(missing_data)
            self.data["last_loaded"] = datetime.now()
        else:
            logger.info("data do not exist")
            self.data["created"] = datetime.now()
        logger.info("filling missing with defaults (most of the time, should be none)")
        self.data.update({k: v for k, v in defaults.items() if k not in self.data})
        self.update()
        logger.info(f"fully initialised, looks like {self.data}")

    def save(self):
        """Dump the data. Don't do this if proband ID is TEST."""
        logger.info("called save()")
        if self.data["proband_id"].upper() not in forbidden_ids:
            self._backup()
            logger.info("saving the data")
            self.data["saved"] = datetime.now()
            dump(self.data, open(self.data["path"], "wb"))
        else:
            logger.info("not saving the data (forbidden ID)")
        self.update()

    def update(self):
        """Updates the attributes according to the internal dictionary."""
        logger.info("called update()")
        self.__dict__.update(self.data)

    def delete(self):
        """Delete the proband from disk."""
        logger.info("called delete()")
        self._backup()
        if exists(self.data["path"]):
            remove(self.data["path"])

    def _backup(self):
        """Make a backup."""
        pass
        # logger.info("called _backup()")
        # if exists(self.data["path"]):
        #     logger.warning("making a backup of previously saved data")
        #     path = self.path.replace("current", "old")
        #     for i in range(8, 0, -1):
        #         path_ = path + f".{i}"
        #         if exists(path_):
        #             move(path_, path + f"{i + 1}")
        #     move(self.path, path + ".1")