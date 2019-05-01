"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import logging

import foreanalyzer._internal_utils as internal
import foreanalyzer.algo_components as alco
import foreanalyzer.exceptions as exc
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.algo")


# ================================= ALGORITHM =================================
# BaseAlgorithm to configure with arguments:
# indicators:
#     [['SMA', [10], 'above'], ...]
# ================================= ALGORITHM =================================

class BaseAlgorithmToConf(object):
    """Algorithm abstract implementation"""

    def __init__(self, currencies, range_of_values, indicators):
        for indicator in indicators:
            if indicator[0] not in [x for x in alco.IndicatorFactory.keys()]:
                raise exc.IndicatorNotListed(indicator[0])
        self.currencies = [internal.conv_str_enum(curr, internal.CURRENCY)
                           for curr in currencies]
        self._data_handler = DataHandler(range_of_values)
        self.stock_data = self._data_handler.dataframes
        self._indicators_conf = indicators
        self.indicators = [indicator[0] for indicator in self._indicators_conf]
        self.instruction = {}
        self.dataframes = {}
        self.status = alco.STATUS.OFF
        LOGGER.debug("BaseAlgorithmToConf inited")

    def setup(self):
        for currency in self.currencies:
            self.stock_data[currency].load()
        self._init_dataframes()
        self._init_indicators()
        self._execute_indicators()
        self.status = alco.STATUS.EXECUTED
        LOGGER.debug("BaseAlgorithmToConf setup")

    def get_datetime_trades(self, currency):
        """get full dataframe"""
        if self.status != alco.STATUS.EXECUTED:
            raise exc.AlgorithmNotExecuted()
        df = self.dataframes[currency]
        indicator_dates = df.data.index
        for indicator_name in self.indicators:
            LOGGER.debug(f"filtering for {indicator_name}")
            indicator = getattr(df, indicator_name)
            indicator_dates = indicator_dates.intersection(
                indicator.execute_filter(self.instruction[indicator_name]))
            LOGGER.debug(f"ultimate dates filtered to {len(indicator_dates)}")
        return indicator_dates

    def _init_dataframes(self):
        """update old df to new algodataframe"""
        for currency in self.currencies:
            df = alco.AlgoDataframe(currency, self.stock_data[currency].data)
            self.dataframes[currency] = df

    def _init_indicators(self):
        """setup all indicators in dataframes"""
        for currency in self.currencies:
            LOGGER.debug(f"setting indicators for {currency.value}")
            df = self.dataframes[currency]
            for indicator in self._indicators_conf:
                LOGGER.debug(f"setting {indicator} for {currency}")
                setattr(df, indicator[0], alco.IndicatorFactory[indicator[0]](
                    df.data, *indicator[1]))
                if indicator[2] not in alco.FilterFactory:
                    raise exc.IndicatorError()
                self.instruction[indicator[0]] = indicator[2]
                LOGGER.debug(f"{indicator[0]} indicator setup with "
                             f"{indicator[1]} with {indicator[2]}")

    def _execute_indicators(self):
        """execute all indicators"""
        for currency in self.currencies:
            for indicator in self.indicators:
                LOGGER.debug(f"executing {indicator} for {currency}")
                getattr(self.dataframes[currency], indicator).execute()


class BaseAlgorithmConfigured(BaseAlgorithmToConf):
    """Algorithm abstract class configured from configuration file"""

    def __init__(self, name):
        config = internal.read_config()
        if name not in config.keys():
            raise ValueError(f"{name} not in config")
        self.config = config[name]
        currencies = self.config['currencies']
        range_of_values = self.config['range_of_values']
        indicators = [[indicator['name'], [arg for _, arg in indicator[
            'arguments'].items()], indicator['scope']] for indicator in
                      self.config['indicators']]
        super().__init__(currencies, range_of_values, indicators)
        LOGGER.debug("Algorithm with preconfigured file inited")


# ============================== REAL ALGORITHM ===============================

class SimpleAlgorithm001(BaseAlgorithmConfigured):
    """Simple Moving Average"""

    def __init__(self):
        super().__init__(self.__class__.__name__)
        LOGGER.debug(f"SimpleAlgorithm001 inited")


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
