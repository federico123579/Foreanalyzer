"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all ABS for algorithm building
"""

import logging
from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd

import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import STATUS

LOGGER = logging.getLogger("foreanalyzer.algo_components")


# ================================ INDICATOR ==================================
# BaseAbstractClass for Indicator with execute for calculating process
# ================================ INDICATOR ==================================

class Indicator(metaclass=ABCMeta):
    """Indicator abstract implementation"""

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()
        self.values = None
        self.status = STATUS.OFF

    @abstractmethod
    def _execute(self):
        """execute calculations"""

    def execute(self):
        """execute calculations and procedures"""
        values = self._execute()
        self.status = STATUS.EXECUTED
        return values


class PeriodIndicator(Indicator, metaclass=ABCMeta):
    """Indicator with period property"""

    def __init__(self, dataframe, period):
        Indicator.__init__(self, dataframe)
        self.period = period

    @abstractmethod
    def _execute(self):
        pass


class IndicatorReduced(Indicator, metaclass=ABCMeta):
    """Indicator reduced"""

    def __init__(self, dataframe, reducer_class, params):
        Indicator.__init__(self, dataframe)
        self.reducer = reducer_class(dataframe, *params)
        self.full_dataframe = None

    @abstractmethod
    def _execute(self):
        pass

    @abstractmethod
    def get_full_dataframe(self):
        """return full dataframe"""


# ================================== FILTER ===================================
# Filter for conditions for making order
# Inherited from an Indicator.
# ================================== FILTER ===================================

class AboveBelowFilter(Indicator, metaclass=ABCMeta):
    """filter for up and down with linear indicator"""

    def __init__(self, dataframe):
        Indicator.__init__(self, dataframe)
        np.warnings.filterwarnings('ignore')

    def above(self):
        """if above than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.greater(self.dataframe['close'], self.values)

    def above_equal(self):
        """if above or equal than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.greater_equal(self.dataframe['close'], self.values)

    def below(self):
        """if below than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.less(self.dataframe['close'], self.values)

    def below_equal(self):
        """if above or equal than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.less_equal(self.dataframe['close'], self.values)

    @abstractmethod
    def _execute(self):
        """execute calculations"""


# ================================== TRIGGER ==================================
# Trigger that set the event which make the order
#
# - I trigger possono essere molteplici nell'algoritmo perché possono esserci
#   più condizioni perché un trade diventi vantaggioso.
# - Possono essere periodici (tipo compra ogni ora) o event-driven (tipo
#   compra quando si verifica una determinata circostanza) ma comunque un
#   trigger dovrà controllare in modo periodico la situazione della borsa.
# - Si scremano i dati in base a ciò che individua l'algoritmo nel periodo
#   di controllo del trigger (quindi si eliminano i valori di intervallo più
#   brevi del'attesa del trigger.
# ================================== TRIGGER ==================================

# ================================== REDUCER ==================================
# reduce data analysis of an indicator to precise time period
# ================================== REDUCER ==================================

class Reducer(Indicator, metaclass=ABCMeta):
    """abstract trigger"""

    def __init__(self, dataframe):
        Indicator.__init__(self, dataframe)
        self.status = STATUS.OFF

    @abstractmethod
    def _execute(self):
        """execute calculations"""


class PeriodReducer(Reducer):
    """simple period reducer"""

    def __init__(self, dataframe, interval):
        """
        :param interval: time in seconds
        """
        Reducer.__init__(self, dataframe)
        self.interval = int(interval)
        LOGGER.debug(f"SimplePeriodTrigger inited with interval of {interval}")

    # noinspection PyTypeChecker
    def _execute(self):
        timestamp = self.dataframe['timestamp']
        while any(timestamp.diff().dropna().dt.seconds < self.interval):
            # get temp series with new index of timestamps
            tm = timestamp[timestamp.diff().dt.seconds <
                           self.interval].reset_index()
            if len(tm) == 1:  # drop last value
                tm.drop(0)
            else:  # drop values even so do not delete all next
                timestamp.drop(
                    tm[tm.index.map(lambda x: int(x) % 2 == 0)]['index'],
                    inplace=True)
        self.dataframe = self.dataframe.iloc[timestamp.index]
        LOGGER.debug(f"SimplePeriodTrigger executed and reduced to "
                     f"{len(self.dataframe)}")
        return self.dataframe


# ============================== REAL INDICATOR ===============================

class SMA(PeriodIndicator, IndicatorReduced, AboveBelowFilter):
    """Simple Moving Average"""

    def __init__(self, dataframe, period, timeframe):
        """
        :param period: int number
        :param timeframe: int number of seconds
        """
        PeriodIndicator.__init__(self, dataframe, period)
        IndicatorReduced.__init__(self, dataframe, PeriodReducer, [timeframe])
        AboveBelowFilter.__init__(self, dataframe)
        LOGGER.debug(f"SMA inited with period {period} and timeframe of "
                     f"{timeframe}")

    def _execute(self):
        df = self.reducer.execute()
        self.values = df['close'].rolling(self.period).mean()
        LOGGER.debug("SMA executed")
        return self.values

    def get_full_dataframe(self):
        if self.status != STATUS.EXECUTED:
            raise exc.IndicatorNotExecuted()
        df = pd.concat([self.dataframe['timestamp'], self.values],
                       axis=1).ffill()
        df.index = df['timestamp']
        df.drop('timestamp', axis=1, inplace=True)
        self.full_dataframe = df
        return df


# ================================= FACTORIES =================================

IndicatorFactory = {
    'SMA': SMA
}


# ============================== ALGO DATAFRAMES ==============================
# algo dataframes for analysis of dataframes with indicators
# ============================== ALGO DATAFRAMES ==============================

class AlgoDataframe(object):
    """dataframe for algo analysis"""

    def __init__(self, currency, data):
        self.currency = currency
        self.data = data
        self.instruction = {}
