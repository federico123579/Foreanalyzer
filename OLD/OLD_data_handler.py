"""
foreanalyzer.data_handler
~~~~~~~~~~~~~~~~~~~~~~~~~

Load data from csv files.
"""

import os.path
import pickle
import time

from progress.spinner import Spinner
import pandas as pd

import foreanalyzer._internal_utils as internal
from foreanalyzer.cli import CliConsole
from foreanalyzer.api_handler import ApiClient

LOGGER = CliConsole()
LOGGER.prefix = "data_handler"


def normalise_df(df, range_of_values):
    """normalise according to written instructions - see README"""
    if range_of_values < len(df):
        df = df.iloc[-range_of_values:].copy()
        LOGGER.debug("dataframe sliced")
    else:
        LOGGER.debug("dataframe not sliced")
    _spin = Spinner("normalising df... ")
    df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
    _spin.next()
    timestamp = pd.Series(
        df['dtyyyymmdd'].map(str) + df['time'].map(str).apply(
            lambda x: (6 - len(x)) * '0') + df['time'].map(str))
    _spin.next()
    df.insert(0, 'datetime', timestamp.map(pd.Timestamp))
    _spin.next()
    df.drop(columns=['ticker', 'vol', 'dtyyyymmdd', 'time'], inplace=True)
    _spin.next()
    df.set_index('datetime', inplace=True)
    _spin.finish()
    LOGGER.debug("dataframe normalised")
    return df


class CSVDataframe(object):
    """hold pandas dataframe object from csv files"""

    def __init__(self, currency, range_of_values: int):
        if currency not in internal.ACC_CURRENCIES:
            raise ValueError("Instrument not accepted")
        self._folder = os.path.join(internal.FOLDER_PATH, 'data')
        self._parent_folder = os.path.join(internal.OUTER_FOLDER_PATH, 'data')
        self.currency = currency
        self.range_of_values = range_of_values
        self.data = None

    def get_pickle_path(self):
        """return the name of the file, accessed from cache"""

    def load(self):
        """load the dataframe with data from a CSV file and save or load
        to/from pickle files stored in cache, loaded dataframes are
        normalised"""
        # load from cache
        file_name = f"{self.currency}_{self.range_of_values}.pickle"
        p_file_path = os.path.join(internal.FOLDER_PATH, 'cache', file_name)
        if os.path.isfile(p_file_path):
            LOGGER.debug(f"{file_name} found")
            with open(p_file_path, 'rb') as f:
                df = pickle.load(f)
        else:
            LOGGER.debug(f"{file_name} pickle not found")
            internal.unzip_data(self._parent_folder, self.currency)
            file_path = os.path.join(
                self._folder, self.currency + '.csv')
            df = normalise_df(pd.read_csv(file_path), self.range_of_values)
            # save cache
            with open(p_file_path, 'wb') as f:
                pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
        self.data = df
        return df

    def unload(self):
        """free RAM"""
        del self.data
        self.data = None


class XTBDataframe(CSVDataframe):
    """check last values using api"""

    def __init__(self, currency, timeframe, time_past):
        super().__init__(currency, None)
        self.timeframe = timeframe
        self.time_past = time_past

    def load(self):
        """load from api"""
        ApiClient().setup()
        _spin = Spinner("normalising xtb df... ")
        raw_values = ApiClient().api.get_chart_last_request(
            self.currency, self.timeframe // 60, time.time() - self.time_past)
        _spin.next()
        values = raw_values['rateInfos']
        datetimes = [pd.to_datetime(x['ctm'] / 1000, unit='s').tz_localize(
            'UTC').tz_convert('Europe/Berlin') for x in values]
        _spin.next()
        opens = [x['open'] / 10 ** raw_values['digits'] for x in values]
        _spin.next()
        closes = [(x['close'] + x['open']) / 10 ** raw_values['digits'] for x
                   in values]
        _spin.next()
        high = [(x['high'] + x['open']) / 10 ** raw_values['digits'] for x in
                 values]
        _spin.next()
        low = [(x['low'] + x['open']) / 10 ** raw_values['digits'] for x in
                values]
        _spin.next()
        candles_df = pd.DataFrame(data={'datetime': datetimes, 'open': opens,
                                  'close': closes, 'high': high, 'low': low})
        _spin.next()
        candles_df.set_index('datetime', inplace=True)
        _spin.finish()
        self.data = candles_df
        return candles_df


class CSVDataHandler(object):
    """handle CSVDataframe objects
    main controller for CSVDataframe objects"""

    def __init__(self, range_of_values: int):
        self.dataframes = {}
        self.range_of_values = range_of_values
        for currency in internal.ACC_CURRENCIES:
            self.dataframes[currency] = CSVDataframe(
                currency, range_of_values)


class XTBDataHandler(object):
    """handle XTBDataframe objects"""

    def __init__(self, timeframe: int, time_past: int):
        self.dataframes = {}
        self.timeframe = timeframe
        self.time_past = time_past
        for currency in internal.ACC_CURRENCIES:
            self.dataframes[currency] = XTBDataframe(
                currency, timeframe, time_past)
