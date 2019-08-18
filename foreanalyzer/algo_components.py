"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all indicators.
"""

import abc
import logging

import numpy as np
import pandas as pd

import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import LoggingContext, resample_business

LOGGER = logging.getLogger("foreanalyzer.algo_components")


# ============================= INDICATOR ===============================
# BaseAbstractClass for Indicator with execute for calculating process
# ============================= INDICATOR ===============================

class Indicator(metaclass=abc.ABCMeta):
    """Base class for financial tools (Indicators)"""

    def __init__(self, dataframe):
        self.column_name: str
        self.dataframe_original = dataframe.copy()
        self.values = None
        self.dataframe_reduced = None
        self.dataframe_reindexed = None
        self.status = {'exe': 0, 'reduced': 0, 'reduced_freq': None}

    @abc.abstractmethod
    def _execute(self, *args):
        """Execute calculations"""

    def _reindex_data(self, *args):
        """Return full dataframe"""
        return self.values.reindex(
            self.dataframe_original.index).ffill()

    def reduce(self, timeframe):
        """Redute to timeframe (expressed in seconds)
        Reduce cut the dataframe leaving fixed intervals
        between each entry"""
        if not isinstance(timeframe, int):
            raise ValueError("timeframe refers to int seconds")
        df = self.dataframe_original.copy()
        df = resample_business(df, timeframe)
        self.dataframe_reduced = df.copy()
        self.status['reduced_freq'] = timeframe
        self.status['reduced'] = 1
        LOGGER.debug(f"reduced to {len(df)} as "
                     f"{timeframe}s timeframe")
        return df

    def reindex_data(self):
        """Reindex data under frequency
        Merge old data with new one and fill blank spaces with previous
        Optimal strategy for mergin future indicators"""
        if not self.status['exe']:
            raise exc.IndicatorNotExecuted()
        df = self._reindex_data()
        del self.dataframe_reduced
        self.dataframe_reduced = None
        # here df is not copied to save some RAM
        self.dataframe_reindexed = df
        self.status['reduced'] = 0
        LOGGER.debug(f"{self.__class__.__name__} reindexed")
        return df

    def submit(self):
        """Execute calculations and procedures
        Execute the core calculation of the indicator and make a new
        pandas series of values than can be reindexed and mixed with
        others ready to be filtered out"""
        values = self._execute()
        self.status['exe'] = 1
        LOGGER.debug(f"{self.__class__.__name__} submitted")
        return values


# =========================== REAL INDICATOR ============================
# Real implementation of indicators.
# =========================== REAL INDICATOR ============================

class SMA(Indicator):
    """Simple Moving Average"""

    def __init__(self, dataframe, period, timeframe):
        """:param period: int number
           :param timeframe: int number of seconds"""
        # indicator parameters
        self.period = period
        self.timeframe = timeframe
        # name of new df column
        self.column_name = f'sma_{self.period}'
        super().__init__(dataframe)
        LOGGER.debug(f"SMA inited with period {period} and timeframe of "
                     f"{timeframe}")

    def _execute(self):
        df = self.reduce(self.timeframe)
        self.values = df['close'].rolling(
            self.period).mean().rename(self.column_name)
        return self.values


class EMA(Indicator):
    """Exponential Moving Average, from a SMA"""

    def __init__(self, dataframe, period, timeframe):
        """:param period: int number
           :param timeframe: int number of seconds"""
        # indicator parameters
        self.period = period
        self.timeframe = timeframe
        self.multiplier = 2 / (self.period + 1)
        # name of new df column
        self.column_name = f'ema_{self.period}'
        super().__init__(dataframe)
        with LoggingContext(LOGGER, level=logging.ERROR):
            self.sma = SMA(dataframe, period, timeframe)
        LOGGER.debug(f"EMA inited with period {period} and timeframe of "
                     f"{timeframe}")

    def _execute(self):
        with LoggingContext(LOGGER, level=logging.ERROR):
            self.sma.submit()
        df = self.reduce(self.timeframe)
        self.values = df['close'].ewm(com=self.period).mean().rename(
            self.column_name)
        return self.values


class BolligerBands(Indicator):
    """Bolliger Bands indicator"""

    def __init__(self, dataframe, timeframe, period=20, multiplier=2):
        """:param period: int number
           :param timeframe: int number of seconds"""
        # indicator parameters
        self.period = period
        self.timeframe = timeframe
        self.multiplier = multiplier
        # name of new df column
        self.column_name = f'BollBands_{self.period}'
        super().__init__(dataframe)
        LOGGER.debug(f"Bolliger Bands inited period: {period} "
                     f"timeframe: {timeframe} multiplier: {multiplier}")

    def _execute(self):
        df = self.reduce(self.timeframe)
        t_price = (df['high'] + df['low'] + df['close']) / 3
        ma_series = t_price.rolling(self.period).mean()
        std_series = t_price.rolling(self.period).apply(np.std, raw=True)
        bol_up = ma_series + self.multiplier * std_series
        bol_dw = ma_series - self.multiplier * std_series
        self.values = pd.DataFrame(data={f'{self.column_name}_up': bol_up,
                                         f'{self.column_name}_down': bol_dw})
        return self.values


# ============================== FACTORIES ==============================
# This factory serves as a link to indicator for string_to_object
# initialization and execution.
# ============================== FACTORIES ==============================

IndicatorFactory = {
    'SMA': SMA,
    'EMA': EMA,
    'BOLL': BolligerBands
}


# =========================== ALGO DATAFRAMES ===========================
# Dataframe object for storing all indicators data in it.
# =========================== ALGO DATAFRAMES ===========================

class AlgoDataframe(object):
    """dataframe for algo analysis"""

    def __init__(self, currency, dataframe):
        self.currency = currency
        self.dataframe = dataframe
        self.indicator_names = []
        self._indicator_list = []  # list for future recall

    def add_indicator(self, name):
        self.indicator_names.append(name)

    def merge_indicators(self):
        """Merge indicators in each dataframe creating more columns"""
        # update list of indicators to recall
        if len(self.indicator_names) != len(self._indicator_list):
            for name in self.indicator_names:
                self._indicator_list.append(getattr(self, name))
        for indicator in self._indicator_list:
            indicator_reindexed = indicator.reindex_data()
            if isinstance(indicator_reindexed, pd.Series):
                self.dataframe[indicator.column_name] = indicator_reindexed
            elif isinstance(indicator_reindexed, pd.DataFrame):
                for column in indicator_reindexed:
                    self.dataframe[column] = indicator_reindexed[column]
        return self.dataframe

    def resample(self, timeframe_seconds):
        """Resample dataframe and return"""
        return resample_business(self.dataframe, timeframe_seconds)

