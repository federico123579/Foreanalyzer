"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import abc

import pandas

from foreanalyzer._internal_utils import (ACC_TIMEFRAMES, ACC_CURRENCIES)
from foreanalyzer.exceptions import PeriodNotExpected

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.algo")


class AbstractAlgorithm(abc.ABCMeta):
    """abstract algo"""

    def __init__(self, timeframe, acc_instrums, period):
        # timeframe of algo (1h, 1d, 10m, ...)
        if timeframe not in ACCEPTED_TIMEFRAMES:
            raise ValueError("timeframe not accepted")
        self.timeframe = timeframe
        # accepted instuments
        for instr in acc_instrums:
            if instr not in ACC_CURRENCIES:
                raise ValueError("insturment {} not accepted".format(instr))
        self.accepted_instruments = acc_instrums
        # time interval of data feed
        if not isinstance(period, int)
        self.period = period

    def check_period(self, period_of_values):
        if len(period_of_values) != self.period:
            raise PeriodNotExpected()
        else:
            self.check_method(period_of_values)

    @abc.abstractclassmethod
    def check_method(self):
        pass



#~~~~~~~~~~~~#
# ALGO TOOLS #
#~~~~~~~~~~~~#

class base_tool(abc.ABCMeta):
    def __init__(self):
        pass


class SMA(base_tool):
    def __init__(self, ):
        self.
