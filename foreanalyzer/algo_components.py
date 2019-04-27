"""
Foreanalyzer.algo_components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains all ABS for algorithm building
"""

from abc import ABCMeta, abstractmethod

import numpy as np

import foreanalyzer.exceptions as exc


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
