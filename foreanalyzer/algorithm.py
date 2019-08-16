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


# ============================== ALGORITHM ==============================
# BaseAlgorithm configured from config.yml
# ============================== ALGORITHM ==============================

class BaseAlgorithm(object):
    """Base Algorithm implementation, read conf from imput"""

    def __init__(self, name: str, indicators: list):
        """
        indicator must be a list like this:
            indicators = [{'name': "SMA", 'args':
                             {'period': .., 'timeframe': ..}}]
        """
        config = internal.read_config()
        if name not in config.keys():
            raise ValueError(f"{name} not in config")
        for indi in indicators:
            if indi['name'] not in alco.IndicatorFactory.keys():
                raise exc.IndicatorNotListed(indi)
        self.config = config[name]
        currencies = self.config['currencies']
        range_of_values = self.config['range_of_values']
        self.currencies = [internal.conv_str_enum(curr, internal.CURRENCY)
                           for curr in currencies]
        self._data_handler = DataHandler(range_of_values)
        self._indicators = indicators
        self._stock_data = self._data_handler.dataframes
        self.dataframes = {}
        self.status = {'exe': 0}
        LOGGER.debug("BaseAlgorithm inited")

    def setup(self):
        """setup for the algo, init and execute indicators"""
        for currency in self.currencies:
            self.dataframes[currency] = alco.AlgoDataframe(
                currency, self._stock_data[currency].load())
        self._init_indicators()
        self._execute_indicators()
        self.status['exe'] = 1
        LOGGER.debug("BaseAlgorithm setup")

    def get_datetime_trades(self, currency):
        """get full dataframe"""
        if not self.status['exe']:
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

    def _init_indicators(self):
        """init indicators here"""
        for currency in self.currencies:
            for indicator in self._indicators:
                dataframe_obj = self.dataframes[currency]
                name = indicator['name']
                setattr(dataframe_obj, name, alco.IndicatorFactory[name](
                    dataframe_obj.dataframe,  **indicator['args']))

    def _execute_indicators(self):
        """execute all indicators"""
        for currency in self.currencies:
            for indicator in self._indicators:
                LOGGER.debug(f"executing {indicator['name']} for {currency}")
                getattr(self.dataframes[currency], indicator['name']).submit()

