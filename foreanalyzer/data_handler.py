"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

Load data from csv files.
"""

import logging
import os.path

import pandas as pd

import foreanalyzer._internal_utils

LOGGER = logging.getLogger("foreanalyzer.data")


def normalise_df(df, range_of_values):
    """normalise according to written instructions - see README"""
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
    LOGGER.debug("dataframe normalised")
    return df


class Dataframe(object):
    """hold pandas  dataframe object from csv files"""

    def __init__(self, currency, range_of_values: int):
        if currency not in foreanalyzer._internal_utils.CURRENCY:
            raise ValueError("Instrument not accepted")
        self._folder = os.path.join(
            foreanalyzer._internal_utils.FOLDER_PATH, 'data')
        self._parent_folder = os.path.join(
            foreanalyzer._internal_utils.OUTER_FOLDER_PATH, 'data')
        self.currency = currency
        self.range_of_values = range_of_values
        self.data = None

    def load(self):
        """load the dataframe with data"""
        foreanalyzer._internal_utils.unzip_data(self._parent_folder,
                                                self.currency.value)
        file_path = os.path.join(self._folder, self.currency.value + '.csv')
        df = normalise_df(pd.read_csv(file_path), self.range_of_values)
        self.data = df
        return df

    def unload(self):
        """free RAM"""
        del self.data
        self.data = None


class DataHandler(object):
    """handle Dataframe obejcts"""

    def __init__(self, range_of_values: int):
        self.dataframes = {}
        self.range_of_values = range_of_values
        for currency in foreanalyzer._internal_utils.CURRENCY:
            self.dataframes[currency] = Dataframe(currency, range_of_values)

