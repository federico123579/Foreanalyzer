"""
foreanalyzer.engine
~~~~~~~~~~~~~~~~~~~~~~~

Main engine for the simulation.
"""

import abc
import os

from foreanalyzer._internal_utils import (ACC_CURRENCIES, OUTER_FOLDER_PATH,
                                          unzip_data)
from foreanalyzer.simulation import AccountSimulated

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.engine")


class EngineBridge(object):
    """engine"""

    def __init__(self):
        # unzip files
        self.feeder = ZipFeeder(os.path.join(OUTER_FOLDER_PATH, 'data'))
        self.feeder.normalize_data()
        # init simulation components
        self.account = AccountSimulated()


class Feeder(metaclass=abc.ABCMeta):
    """abstract implementation of Feeder of data"""

    @abc.abstractmethod
    def normalize_data(self):
        pass


class ZipFeeder(Feeder):
    """create data from zip file outer folder"""

    def __init__(self, folder):
        self.basefolder = folder

    def normalize_data(self):
        for instr in ACC_CURRENCIES:
            unzip_data(self.basefolder, instr.value)
