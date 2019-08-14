"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all ABS for algorithm building
"""

import abc
import logging

import pandas as pd

import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import STATUS

LOGGER = logging.getLogger("foreanalyzer.algo_components")


# ================================ INDICATOR ==================================
# BaseAbstractClass for Indicator with execute for calculating process
# WARNING: IndicatorReduced must be the last to init in indicator init
# ================================ INDICATOR ==================================

class Indicator(metaclass=abc.ABCMeta):
    """Indicator abstract implementation"""

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()
        self.values = None
        self.date_dataframe = None
        self.status = STATUS.OFF

    @abc.abstractmethod
    def _execute(self):
        """execute calculations"""

    @abc.abstractmethod
    def reindex_date(self):
        """return full dataframe"""

    def execute(self):
        """execute calculations and procedures"""
        values = self._execute()
        self.status = STATUS.EXECUTED
        return values


class IndicatorReduced(Indicator, metaclass=abc.ABCMeta):
    """Indicator reduced"""

    def __init__(self, dataframe, reducer_class, params):
        Indicator.__init__(self, dataframe)
        self.reducer = reducer_class(dataframe, *params)
        self.former_dataframe = None

    @abc.abstractmethod
    def _execute(self):
        """execute calculations"""

    @abc.abstractmethod
    def reindex_date(self):
        """return full dataframe"""

    def execute(self):
        """reduce and execute calculations and procedures"""
        self.former_dataframe = self.dataframe
        self.dataframe = self.reducer.execute()
        return Indicator.execute(self)


class IndicatorFiltered(object):
    """Indicator filtered"""

    def __init__(self, dataframe):
        self.filter = Filter(dataframe)

    def update_filter(self, values):
        """call Filter.update method"""
        return self.filter.update(values)

    def execute_filter(self, scope):
        """call Filter.execute method"""
        return self.filter.execute(scope)


# ================================== FILTER ===================================
# Filter for conditions for making order
# Inherited from an Indicator.
# ================================== FILTER ===================================

def filter_above(dataframe, values):
    """check if close price is above indicator"""
    df = pd.concat([dataframe, values], axis=1)
    return df[df['close'] > df[values.name]].index


def filter_above_equal(dataframe, values):
    """check if close price is above indicator"""
    df = pd.concat([dataframe, values], axis=1)
    return df[df['close'] >= df[values.name]].index


def filter_below(dataframe, values):
    """check if close price is above indicator"""
    df = pd.concat([dataframe, values], axis=1)
    return df[df['close'] < df[values.name]].index


def filter_below_equal(dataframe, values):
    """check if close price is above indicator"""
    df = pd.concat([dataframe, values], axis=1)
    return df[df['close'] <= df[values.name]].index


FilterFactory = {
    'above': filter_above,
    'above_equal': filter_above_equal,
    'below': filter_below,
    'below_equal': filter_below_equal
}


class Filter(metaclass=abc.ABCMeta):
    """base abstract class for filters"""

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.values = None
        self.status = STATUS.OFF

    def update(self, values):
        """update status"""
        self.values = values
        self.status = STATUS.EXECUTED

    def execute(self, scope):
        """return datetime index of advantageous time"""
        if self.status != STATUS.EXECUTED:
            raise exc.IndicatorNotExecuted()
        if scope not in FilterFactory.keys():
            raise ValueError(f"{scope} not listed in filter")
        filtered = FilterFactory[scope](self.dataframe, self.values)
        LOGGER.debug(f"filtered to {len(filtered)}")
        return filtered


# ================================== REDUCER ==================================
# reduce data analysis of an indicator to precise time period
# ================================== REDUCER ==================================

class Reducer(metaclass=abc.ABCMeta):
    """abstract reducer"""

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()
        self.values = None
        self.status = STATUS.OFF

    @abc.abstractmethod
    def _execute(self):
        """execute calculations"""

    def execute(self):
        """execute calculations and procedures"""
        values = self._execute()
        self.status = STATUS.EXECUTED
        return values


class PeriodReducer(Reducer):
    """simple period reducer"""

    def __init__(self, dataframe, interval):
        """
        :param interval: time in seconds
        """
        Reducer.__init__(self, dataframe)
        self.interval = int(interval)
        LOGGER.debug(f"PeriodReducer inited with interval of {interval}")

    def _execute(self):
        self.dataframe = self.dataframe.resample(f'{self.interval}S').asfreq()
        LOGGER.debug(f"SimplePeriodTrigger executed and reduced to "
                     f"{len(self.dataframe)}")
        return self.dataframe


# ============================== REAL INDICATOR ===============================

class SMA(IndicatorReduced, IndicatorFiltered):
    """Simple Moving Average"""

    def __init__(self, dataframe, period, timeframe):
        """
        :param period: int number
        :param timeframe: int number of seconds
        """
        self.name = "sma"
        IndicatorReduced.__init__(self, dataframe, PeriodReducer, [timeframe])
        IndicatorFiltered.__init__(self, dataframe)
        # indicator properties
        self.period = period
        LOGGER.debug(f"SMA inited with period {period} and timeframe of "
                     f"{timeframe}")

    def _execute(self):
        self.values = self.dataframe['close'].rolling(
            self.period).mean().rename(self.name)
        LOGGER.debug("SMA executed")
        self.update_filter(self.values)
        return self.values

    def reindex_date(self):
        if self.status != STATUS.EXECUTED:
            raise exc.IndicatorNotExecuted()
        df = self.values.reindex(self.former_dataframe.index).ffill()
        self.date_dataframe = df
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
