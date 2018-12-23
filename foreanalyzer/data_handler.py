"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

RAM eater, load RAM.
"""

import abc
import os.path
import time

import pandas as pd

from foreanalyzer._internal_utils import (
    ACC_CURRENCIES, FOLDER_PATH, OUTER_FOLDER_PATH, unzip_data)

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.data")


class DataHandler(object):
    """handler"""

    def __init__(self, range_of_values):
        self.FOLDER = os.path.join(FOLDER_PATH, 'data')
        self.feeder = ZipFeeder(os.path.join(OUTER_FOLDER_PATH, 'data'))
        self.range_of_values = range_of_values
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
        df = normalize_df(pd.read_csv(file_path), self.range_of_values)
        self.data[instrument.value] = df
        return self.data[instrument.value]

    def extract_all(self):
        self.feeder.normalize_data()


def normalize_df(df, range_of_values, time_of_log=10):
    df.drop(df.index[:-range_of_values], inplace=True)
    df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
    old_t = time.time()
    for i, row in enumerate(df.iterrows()):
        if time.time() - old_t > time_of_log:
            LOGGER.debug("{:.3f}% normalized".format(i / len(df) * 100))
            old_t = time.time()
        str_time = str(int(row[1].loc['time']))
        str_date = str(int(row[1].loc['dtyyyymmdd']))
        if len(str_time) < 6:
            str_time = (6 - len(str_time))*'0' + str_time
        timestamp = pd.Timestamp(str_date + str_time)
        df.loc[row[0],'time'] = timestamp
    df.drop(columns=['ticker', 'vol', 'dtyyyymmdd'], inplace=True)
    df.rename({'time': 'timestamp'}, axis='columns', inplace=True)
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
