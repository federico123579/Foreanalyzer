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
# This object when called for setup init a list of indicators with their
# respective parameters and after having set up a personalized instace
# of each of them in a respective dataframe object call them and submit.
# Doing this every indicator is inited and executed on setup and given
# access from dataframe object.
# ============================== ALGORITHM ==============================

class BaseAlgorithm(object):
    """Base Algorithm implementation
    Read conf from imput and accept indicators and args for them"""

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
                raise exc.IndicatorNotListed(indi['name'])
        self.config = config[name]
        currencies = self.config['currencies']
        range_of_values = self.config['range_of_values']
        self.currencies = [internal.conv_str_enum(curr, internal.CURRENCY)
                           for curr in currencies]
        self._data_handler = DataHandler(range_of_values)
        self._indicators = indicators  # list of indicator configuration
        self._stock_data = self._data_handler.dataframes
        self.dataframes = {}  # store dataframe objects
        self.status = {'exe': 0}
        LOGGER.debug("BaseAlgorithm inited")

    def _init_indicators(self):
        """Init indicators here
        Indicators are inited here and set as attr in dataframe objects
        for each of currencies listened."""
        for currency in self.currencies:
            for indicator in self._indicators:
                dataframe_obj = self.dataframes[currency]
                factory_name = indicator['name']
                LOGGER.debug(f"setting {factory_name} for {currency.value}")
                _indicator = alco.IndicatorFactory[factory_name](
                    dataframe_obj.dataframe, **indicator['args'])
                setattr(dataframe_obj, _indicator.column_name, _indicator)
                dataframe_obj.add_indicator(_indicator.column_name)

    def _execute_indicators(self):
        """Execute all indicators
        Execute all indicators listened in self._indicators, given by
        init and submit their values in dataframe object."""
        for currency in self.currencies:
            df = self.dataframes[currency]
            for indicator in df.indicator_names:
                LOGGER.debug(f"executing {indicator} for {currency}")
                getattr(df, indicator).submit()

    def setup(self):
        """Setup for the algo, init and execute indicators
        Call the setup directives, initing and executing all indicators."""
        for currency in self.currencies:
            self.dataframes[currency] = alco.AlgoDataframe(
                currency, self._stock_data[currency].load())
        self._init_indicators()
        self._execute_indicators()
        self.status['exe'] = 1
        LOGGER.debug("BaseAlgorithm setup")

