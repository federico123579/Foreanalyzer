"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

RAM eater, load RAM.
"""

import abc
import os.path

from foreanalyzer._internal_utils import (ACC_CURRENCIES, OUTER_FOLDER_PATH,
                                          unzip_data)

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.data")


class DataHandler(object):
    """handler"""

    def __init__(self):
        pass

    def get_data(self):
        # unzip files
        self.feeder = ZipFeeder(os.path.join(OUTER_FOLDER_PATH, 'data'))
        self.feeder.normalize_data()

    def load_data(self, instrument):
        if instrument not in ACC_CURRENCIES:
            raise ValueError("Instrument not accepted")


class Feeder(metaclass=abc.ABCMeta):
    """abstract implementation of Feeder of data"""

    def __init__(self):
        self.data = []

    @abc.abstractmethod
    def normalize_data(self):
        pass


class ZipFeeder(Feeder):
    """create data from zip file outer folder"""

    def __init__(self, folder):
        self.basefolder = folder

    def normalize_single(self, instr):
        unzip_data(self.basefolder, instr.value)

    def normalize_data(self):
        for instr in ACC_CURRENCIES:
            self.normalize_single(instr)
