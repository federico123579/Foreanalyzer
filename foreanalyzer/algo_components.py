"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all indicators.
"""

import abc
import logging

import pandas as pd

import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import STATUS

LOGGER = logging.getLogger("foreanalyzer.algo_components")


# ============================= INDICATOR ===============================
# BaseAbstractClass for Indicator with execute for calculating process
# WARNING: IndicatorReduced must be the last to init in indicator init
# ============================= INDICATOR ===============================

class Indicator(metaclass=abc.ABCMeta):
    """abstract implementation"""

    def __init__(self, dataframe):
        self.dataframe_original = dataframe.copy()
        self.values = None
        self.dataframe_reduced = None
        self.dataframe_reindexed = None
        self.status = {'exe': 0, 'reduced': 0, 'reduced_freq': None}

    @abc.abstractmethod
    def _execute(self, *args):
        """execute calculations"""

    @abc.abstractmethod
    def _reindex_data(self, *args):
        """return full dataframe"""

    def reduce(self, timeframe):
        """redute to timeframe (expressed in seconds)"""
        if not isinstance(timeframe, int):
            raise ValueError("timeframe refers to int seconds")
        df = self.dataframe_original.copy()
        df = df.resample(f'{timeframe}S').asfreq()
        self.dataframe_reduced = df.copy()
        self.status['reduced_freq'] = timeframe
        self.status['reduced'] = 1
        LOGGER.debug(f"reduced to {len(df)} as "
                     f"{timeframe}s timeframe")
        return df

    def reindex_data(self):
        """reindex data under frequency"""
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
        """execute calculations and procedures"""
        values = self._execute()
        self.status['exe'] = 1
        LOGGER.debug(f"{self.__class__.__name__} submitted")
        return values


# =========================== REAL INDICATOR ============================

class SMA(Indicator):
    """Simple Moving Average"""

    def __init__(self, dataframe, period, timeframe):
        """
        :param period: int number
        :param timeframe: int number of seconds
        """
        # indicator parameters
        self.period = period
        self.timeframe = timeframe
        # name of new df column
        self.column_name = 'sma'
        super().__init__(dataframe)
        LOGGER.debug(f"SMA inited with period {period} and timeframe of "
                     f"{timeframe}")

    def _execute(self):
        df = self.reduce(self.timeframe)
        self.values = df['close'].rolling(
            self.period).mean().rename(self.column_name)
        return self.values

    def _reindex_data(self):
        df = self.values.reindex(self.dataframe_original.index).ffill()
        return df


# ============================== FACTORIES ==============================

IndicatorFactory = {
    'SMA': SMA
}


# =========================== ALGO DATAFRAMES ===========================
# algo dataframes for analysis of dataframes with indicators
# =========================== ALGO DATAFRAMES ===========================

class AlgoDataframe(object):
    """dataframe for algo analysis"""

    def __init__(self, currency, dataframe):
        self.currency = currency
        self.dataframe = dataframe

