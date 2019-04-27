"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all ABS for algorithm building
"""

import logging
from abc import ABCMeta, abstractmethod

import numpy as np

import foreanalyzer.exceptions as exc

LOGGER = logging.getLogger("foreanalyzer.algo_components")


# ================================ INDICATOR ==================================
# BaseAbstractClass for Indicator with execute for calculating process
# ================================ INDICATOR ==================================

class Indicator(metaclass=ABCMeta):
    """Indicator abstract implementation"""

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.values = None

    @abstractmethod
    def execute(self):
        """execute calculations"""


class PeriodIndicator(Indicator, metaclass=ABCMeta):
    """Indicator with period property"""

    def __init__(self, dataframe, period):
        super().__init__(dataframe)
        self.period = period

    @abstractmethod
    def execute(self):
        pass


# ================================== FILTER ===================================
# Filter for conditions for making order
# ================================== FILTER ===================================

class UpDownFilter(Indicator, metaclass=ABCMeta):
    """filter for up and down with linear indicator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        np.warnings.filterwarnings('ignore')

    def greater(self):
        """if greater than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.greater(self.dataframe['close'], self.values)

    def greater_equal(self):
        """if greater or equal than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.greater_equal(self.dataframe['close'], self.values)

    def less(self):
        """if less than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.less(self.dataframe['close'], self.values)

    def less_equal(self):
        """if greater or equal than this indicator"""
        if self.values is None:
            raise exc.IndicatorNotExecuted()
        if len(self.dataframe) != len(self.values):
            raise exc.IndicatorLenError(len(self.values), len(self.dataframe))
        return np.less_equal(self.dataframe['close'], self.values)

    @abstractmethod
    def execute(self):
        """execute calculations"""


# ============================== REAL INDICATOR ===============================

class SMA(PeriodIndicator, UpDownFilter):
    """Simple Moving Average"""

    def __init__(self, dataframe, period):
        PeriodIndicator.__init__(self, dataframe, period)
        UpDownFilter.__init__(self, dataframe)
        LOGGER.debug(f"SMA inited with period {period}")

    def execute(self):
        self.values = self.dataframe['close'].rolling(self.period).mean()
        LOGGER.debug("SMA executed")
        return self.values


# ============================= INDICATOR FACTORY =============================

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
