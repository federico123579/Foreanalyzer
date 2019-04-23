"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import logging

import foreanalyzer.abstract as abstract

LOGGER = logging.getLogger("foreanalyzer.algo")


# ================================ INDICATORS =================================

class SMA(abstract.PeriodIndicator, abstract.UpDownFilter):
    """Simple Moving Average"""

    def __init__(self, dataframe, period):
        abstract.PeriodIndicator.__init__(self, dataframe, period)
        abstract.UpDownFilter.__init__(self, dataframe)
        LOGGER.debug(f"SMA inited with period {period}")

    def execute(self):
        self.values = self.dataframe['close'].rolling(self.period).mean()
        LOGGER.debug("SMA executed")
        return self.values

# ================================ INDICATORS =================================


# import numpy
#
# from foreanalyzer._internal_utils import CURRENCY
# from foreanalyzer.data_handler import DataHandler
# from foreanalyzer.exceptions import PeriodNotExpected
#
#
#
# class AbstractAlgorithm(metaclass=abc.ABCMeta):
#     """abstract algo"""
#
#     def __init__(self, timeframe, acc_instrums, period, range_of_values):
#         # timeframe of algo (1h, 1d, 10m, ...)
#         if timeframe not in ACC_TIMEFRAMES:
#             raise ValueError("timeframe not accepted")
#         self.timeframe = timeframe
#         # accepted instuments
#         for instr in acc_instrums:
#             if instr not in CURRENCY:
#                 raise ValueError("instrument {} not accepted".format(instr))
#         self.accepted_instruments = acc_instrums
#         # time interval of data feed
#         if not isinstance(period, int):
#             raise ValueError("period not an int")
#         self.period = period
#         self.DH = DataHandler(range_of_values)
#         self.data = self.DH.data
#
#     def check_period(self, period_of_values):
#         if len(period_of_values) != self.period:
#             raise PeriodNotExpected()
#         else:
#             self.check_method(period_of_values)
#
#     @abc.abstractmethod
#     def feed(self):
#         pass
#
#     @abc.abstractmethod
#     def analyse(self):
#         pass
#
#
# class AlgorithmExample001(AbstractAlgorithm):
#     def __init__(self):
#         timeframe = ACC_TIMEFRAMES.ONE_HOUR
#         acc_instrums = [CURRENCY.EURUSD]
#         period = 15
#         range_of_values = 50000
#         super().__init__(timeframe, acc_instrums, period, range_of_values)
#         # tools
#         self.sma = SMA(self.period)
#
#     def feed(self):
#         for instr in self.accepted_instruments:
#             # load data from csv
#             LOGGER.debug("loading data...")
#             self.DH.load_data(instr)
#             data = self.data[instr.value]
#             # fix timeframe
#             LOGGER.debug("fixing timeframe...")
#             len_pre_removal = len(data)
#             fix_timeframe(data, self.timeframe)
#             entries_removed = len_pre_removal - len(data)
#             LOGGER.debug("{} entries removed from {} rows".format(
#                 entries_removed, len_pre_removal))
#             # evaluate sma
#             LOGGER.debug("calcolating sma...")
#             data = self.sma.eval(data)
#             # drop NaN
#             len_pre_removal = len(data)
#             data.dropna(inplace=True)
#             nan_removed = len_pre_removal - len(data)
#             LOGGER.debug("NaN removed {} from {} rows".format(
#                 nan_removed, len_pre_removal))
#             return data
#
#     def analyse(self):
#         for instr in CURRENCY:
#             pass
#
#
# #~~~~~~~~~~~~#
# # ALGO TOOLS #
# #~~~~~~~~~~~~#
#
# def fix_timeframe(df, timeframe):
#     for i in range(len(df)):
#         if i+1 < len(df):
#             while calc_diff_tf(df, i) < norm_timeframe(timeframe):
#                 df.drop(df.index[i+1], inplace=True)
#                 if i+1 >= len(df):
#                     break
#
#
# def calc_diff_tf(df, index):
#     return (df.loc[df.index[index+1], 'timestamp'] - df.loc[df.index[index], 'timestamp']).total_seconds()
#
#
# class base_tool(metaclass=abc.ABCMeta):
#     def __init__(self):
#         pass
#
#     @abc.abstractmethod
#     def eval(self):
#         pass
#
#
# class SMA(base_tool):
#     def __init__(self, period):
#         self.period = period
#
#     def eval(self, df):
#         df['sma'] = numpy.nan  # set NaN
#         for i in range(len(df)):
#             i += 1  # scale up
#             # calc other index margin
#             i_p = i - self.period
#             # if n (period) of values avaible
#             if i_p >= 0:
#                 close_index = df.columns.get_loc('close')
#                 # calc simple moving average sum(n1+n2+n3) / nn
#                 sma = sum(df.iloc[i_p:i, close_index]) / self.period
#                 # set sma
#                 df.at[df.index[i - 1], 'sma'] = sma
#         return df
