"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

RAM eater, load RAM.
"""

import logging
import os.path

import pandas as pd

import foreanalyzer._internal_utils

LOGGER = logging.getLogger("foreanalyzer.data")


def normalize_df(df, range_of_values):
    if range_of_values < len(df):
        df = df.iloc[-range_of_values:].copy()
        LOGGER.debug("dataframe sliced")
    else:
        LOGGER.debug("dataframe not sliced")
    df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
    timestamp = pd.Series(
        df['dtyyyymmdd'].map(str) + df['time'].map(str).apply(
            lambda x: (6 - len(x)) * '0') + df['time'].map(str))
    df.insert(0, 'datetime', timestamp.map(pd.Timestamp))
    df.drop(columns=['ticker', 'vol', 'dtyyyymmdd', 'time'], inplace=True)
    df.set_index('datetime', inplace=True)
    LOGGER.debug("dataframe normalized")
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
