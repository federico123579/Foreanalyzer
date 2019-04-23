"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

RAM eater, load RAM.
"""

import logging
import os.path
import time

import numpy as np
import pandas as pd

import foreanalyzer._internal_utils

LOGGER = logging.getLogger("foreanalyzer.data")


def normalize_df(df, range_of_values, time_of_log=10):
    df.drop(df.index[:-range_of_values], inplace=True)
    df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
    old_t = time.time()
    for i, row in enumerate(df.iterrows()):
        if time.time() - old_t > time_of_log:
            LOGGER.debug(f"{i / len(df) * 100:.3f}% normalized")
            old_t = time.time()
        str_time = str(int(row[1].loc['time']))
        str_date = str(int(row[1].loc['dtyyyymmdd']))
        if len(str_time) < 6:
            str_time = (6 - len(str_time))*'0' + str_time
        timestamp = pd.Timestamp(str_date + str_time)
        df.loc[row[0], 'time'] = timestamp
    df.drop(columns=['ticker', 'vol', 'dtyyyymmdd'], inplace=True)
    df.rename({'time': 'timestamp'}, axis='columns', inplace=True)
    df.index = np.arange(len(df))
    return df


class Dataframe(object):
    """Dataframe class"""

    def __init__(self, currency, range_of_values: int):
        if currency not in foreanalyzer._internal_utils.CURRENCY:
            raise ValueError("Instrument not accepted")
        # feeder
        self._folder = os.path.join(
            foreanalyzer._internal_utils.FOLDER_PATH, 'data')
        self.feeder = ZipFeeder(os.path.join(
            foreanalyzer._internal_utils.OUTER_FOLDER_PATH, 'data'))
        self.currency = currency
        self.range_of_values = range_of_values
        self.data = None

    def load(self):
        """load the dataframe with data"""
        self.feeder.normalize_single(self.currency)
        file_path = os.path.join(self._folder, self.currency.value + '.csv')
        df = normalize_df(pd.read_csv(file_path), self.range_of_values)
        self.data = df
        return df

    def unload(self):
        del self.data
        self.data = None


class DataHandler(object):
    """handler"""

    def __init__(self, range_of_values: int):
        self.dataframes = {}
        self.range_of_values = range_of_values
        for currency in foreanalyzer._internal_utils.CURRENCY:
            self.dataframes[currency] = Dataframe(currency, range_of_values)


class ZipFeeder(object):
    """create data from zip file outer folder"""

    def __init__(self, folder):
        self.basefolder = folder

    def normalize_single(self, instr):
        foreanalyzer._internal_utils.unzip_data(self.basefolder, instr.value)
