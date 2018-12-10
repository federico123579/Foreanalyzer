"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

RAM eater, load RAM.
"""

import abc
import os.path

import pandas as pd

from foreanalyzer._internal_utils import (ACC_CURRENCIES, FOLDER_PATH,
                                          OUTER_FOLDER_PATH, unzip_data)

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.data")


class DataHandler(object):
    """handler"""

    def __init__(self):
        self.FOLDER = os.path.join(FOLDER_PATH, 'data')
        self.feeder = ZipFeeder(os.path.join(OUTER_FOLDER_PATH, 'data'))
        self.data = {}

    def get_data(self):
        """!INEFFICIENT!"""
        for instr in ACC_CURRENCIES:
            self.load_data(instr)
        return self.data

    def unload_data(self):
        self.data.clear()

    def load_data(self, instrument):
        if instrument not in ACC_CURRENCIES:
            raise ValueError("Instrument not accepted")
        self.feeder.normalize_single(instrument)
        file_path = os.path.join(self.FOLDER, instrument.value + '.csv')
        df = self._normalize_data(pd.read_csv(file_path))
        self.data[instrument.value] = df
        return self.data[instrument.value]

    def _normalize_data(self, df):
        df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
        return df


class Feeder(metaclass=abc.ABCMeta):
    """abstract implementation of Feeder of data"""

    def __init__(self):
        pass

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
