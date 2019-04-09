"""
Foreanalyzer.newVersion.abstract
~~~~~~~

Contains all ABS for algorithm building
"""

from abc import ABCMeta

from foreanalyzer.newVersion.config import Config


class Algorithm(metaclass=ABCMeta):
    """class for algorithm"""

    def __init__(self):
        pass


# ================================ INDICATORS =================================
# BaseAbstractClass for Indicator and other two classes:
# - Indicator default (with the same dataframe)
# - Indicator dedicated (with dedicated dataframe)
# ================================ INDICATORS =================================

class Indicator(metaclass=ABCMeta):
    """Indicator abstract class"""

    def __init__(self):
        pass


class DefaultIndicator(metaclass=ABCMeta, Indicator):
    """Indicator with same dataframe"""

    def __init__(self, dataframe):
        self.data = dataframe
        super().__init__()


class DedicatedIndicator(metaclass=ABCMeta, Indicator):
    """Indicator with dedicated dataframe"""

    def __init__(self, currency):
        self.data = Dataframe(currency)
        super().__init__()


# ================================== DATAFRAME ================================
# Dataframe with data of currencies.
# =============================================================================

class DataframePool(metaclass=ABCMeta):
    """pool of Dataframes"""

    def __init__(self, currencies):
        self.currencies = currencies



