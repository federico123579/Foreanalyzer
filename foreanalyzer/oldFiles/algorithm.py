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

class RealAlgorithm(BaseAlgorithmConfigured):
    """Simple Moving Average"""

    def __init__(self):
        super().__init__('algo_config')
        LOGGER.debug(f"SimpleAlgorithm001 inited")
