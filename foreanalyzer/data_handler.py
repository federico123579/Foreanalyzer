"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

Load data from csv files.
"""

import logging
import os.path
import pickle
import time

import pandas as pd

import foreanalyzer._internal_utils as internal
from foreanalyzer.api_handler import ApiClient

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
        if currency not in internal.CURRENCY:
            raise ValueError("Instrument not accepted")
        self._folder = os.path.join(internal.FOLDER_PATH, 'data')
        self._parent_folder = os.path.join(internal.OUTER_FOLDER_PATH, 'data')
        self.currency = currency
        self.range_of_values = range_of_values
        self.data = None

    def get_pickle_path(self):
        """return the name of the file, accessed from the efficency module"""
        file_name = f"{self.currency.value}_{self.range_of_values}.pickle"
        return os.path.join(internal.FOLDER_PATH, 'algo_efficency', file_name)

    def load(self):
        """load the dataframe with data"""
        # save file on algo_efficiency
        p_file_path = self.get_pickle_path()
        file_name = os.path.basename(p_file_path).split('.')[0]
        if os.path.isfile(p_file_path):
            LOGGER.debug(f"{file_name} pickle found")
            with open(p_file_path, 'rb') as f:
                df = pickle.load(f)
        else:
            LOGGER.debug(f"{file_name} pickle not found")
            internal.unzip_data(self._parent_folder, self.currency.value)
            file_path = os.path.join(self._folder, self.currency.value + '.csv')
            df = normalise_df(pd.read_csv(file_path), self.range_of_values)
            with open(p_file_path, 'wb') as f:
                pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
        self.data = df
        return df

    def unload(self):
        """free RAM"""
        del self.data
        self.data = None


class LatestDataframe(Dataframe):
    """check last values using api"""

    def __init__(self, currency, timeframe, time_past):
        super().__init__(currency, None)
        self.timeframe = timeframe
        self.time_past = time_past

    def load(self):
        """load from api"""
        ApiClient().setup()
        raw_values = ApiClient().api.get_chart_last_request(
            self.currency.value, self.timeframe // 60, time.time() -
                                                       self.time_past)
        values = raw_values['rateInfos']
        datetimes = [pd.to_datetime(x['ctm'] / 1000, unit='s').tz_localize(
            'UTC').tz_convert('Europe/Berlin') for x in values]
        opens = [x['open'] / 10 ** raw_values['digits'] for x in values]
        closes = [(x['close'] + x['open']) / 10 ** raw_values['digits'] for x
                   in values]
        high = [(x['high'] + x['open']) / 10 ** raw_values['digits'] for x in
                 values]
        low = [(x['low'] + x['open']) / 10 ** raw_values['digits'] for x in
                values]
        candles_df = pd.DataFrame(data={'datetime': datetimes, 'open': opens,
                                  'close': closes, 'high': high, 'low': low})
        candles_df.set_index('datetime', inplace=True)
        self.data = candles_df
        return candles_df


class DataHandler(object):
    """handle Dataframe objects"""

    def __init__(self, range_of_values: int):
        self.dataframes = {}
        self.range_of_values = range_of_values
        for currency in internal.CURRENCY:
            self.dataframes[currency] = Dataframe(currency, range_of_values)


class LatestDataHandler(object):
    """handle LatestDataframe objects"""

    def __init__(self, timeframe: int, time_past: int):
        self.dataframes = {}
        self.timeframe = timeframe
        self.time_past = time_past
        for currency in internal.CURRENCY:
            self.dataframes[currency] = LatestDataframe(currency, timeframe,
                                                        time_past)
