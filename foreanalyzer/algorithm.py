"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import abc

import numpy as np

from foreanalyzer.data_handler import DataHandler
from foreanalyzer._internal_utils import (
    ACC_TIMEFRAMES, ACC_CURRENCIES, MODE, norm_timeframe)
from foreanalyzer.exceptions import PeriodNotExpected

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.algo")


class AbstractAlgorithm(metaclass=abc.ABCMeta):
    """abstract algo"""

    def __init__(self, timeframe, acc_instrums, period, range_of_values):
        # timeframe of algo (1h, 1d, 10m, ...)
        if timeframe not in ACC_TIMEFRAMES:
            raise ValueError("timeframe not accepted")
        self.timeframe = timeframe
        # accepted instuments
        for instr in acc_instrums:
            if instr not in ACC_CURRENCIES:
                raise ValueError("insturment {} not accepted".format(instr))
        self.accepted_instruments = acc_instrums
        # time interval of data feed
        if not isinstance(period, int):
            raise ValueError("period not an int")
        self.period = period
        self.DH = DataHandler(range_of_values)
        self.data = self.DH.data

    def check_period(self, period_of_values):
        if len(period_of_values) != self.period:
            raise PeriodNotExpected()
        else:
            self.check_method(period_of_values)

    @abc.abstractmethod
    def feed(self):
        pass

    @abc.abstractmethod
    def analyse(self):
        pass


class AlgorithmExample001(AbstractAlgorithm):
    def __init__(self, range_of_values):
        timeframe = ACC_TIMEFRAMES.ONE_HOUR
        acc_instrums = [ACC_CURRENCIES.EURUSD]
        period = 15
        super().__init__(timeframe, acc_instrums, period, range_of_values)
        # tools
        self.sma = SMA(self.period)

    def feed(self):
        for instr in self.accepted_instruments:
            # load data from csv
            LOGGER.debug("loading data for {} . . .".format(instr))
            self.DH.load_data(instr)
            data = self.data[instr.value]
            # fix timeframe
            LOGGER.debug("fixing timeframe...")
            len_pre_removal = len(data)
            fix_timeframe(data, self.timeframe)
            entries_removed = len_pre_removal - len(data)
            LOGGER.debug("{} entries removed from {} rows".format(
                entries_removed, len_pre_removal))
            # evaluate sma
            LOGGER.debug("calcolating sma...")
            data = self.sma.eval(data)
            # drop NaN
            len_pre_removal = len(data)
            data.dropna(inplace=True)
            nan_removed = len_pre_removal - len(data)
            LOGGER.debug("NaN removed {} from {} rows".format(
                nan_removed, len_pre_removal))
            return data

    def analyse(self, instr):
        data = self.data[instr.value] # load data
        movs = []
        for i in range(len(data)):
            if data.iloc[i]['close'] > data.iloc[i]['sma']:
                tm = data.iloc[i]['timestamp']
                mode = MODE.BUY
                quantity = 100
                movs.append({'timeframe': tm, 'mode': mode,
                             'quantity': quantity})
        return movs


#~~~~~~~~~~~~#
# ALGO TOOLS #
#~~~~~~~~~~~~#

def fix_timeframe(df, timeframe):
    for i in range(len(df)):
        if i+1 < len(df):
            while calc_diff_tf(df, i) < norm_timeframe(timeframe):
                df.drop(df.index[i+1], inplace=True)
                if i+1 >= len(df):
                    break


def calc_diff_tf(df, index):
    return (df.loc[df.index[index+1], 'timestamp'] - df.loc[df.index[index], 'timestamp']).total_seconds()


class base_tool(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def eval(self):
        pass


class SMA(base_tool):
    def __init__(self, period):
        self.period = period

    def eval(self, df):
        df['sma'] = np.nan  # set NaN
        for i in range(len(df)):
            i += 1  # scale up
            # calc other index margin
            i_p = i - self.period
            # if n (period) of values avaible
            if i_p >= 0:
                close_index = df.columns.get_loc('close')
                # calc simple moving average sum(n1+n2+n3) / nn
                sma = sum(df.iloc[i_p:i, close_index]) / self.period
                # set sma
                df.at[df.index[i - 1], 'sma'] = sma
        return df
