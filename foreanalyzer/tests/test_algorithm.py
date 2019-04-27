"""
test.test_algorithm
~~~~~~~~~~~~~~~~~

Test algos.
"""

import logging

import pytest

import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import CURRENCY
from foreanalyzer.algorithm import SMA, BaseAlgorithmToConf, SimpleAlgorithm001
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
DEFAULT_CURRENCY = CURRENCY.EURUSD
DEFAULT_RANGE = 1000


def test_SMA():
    period = 10
    df = DataHandler(1000).dataframes[DEFAULT_CURRENCY].load()
    sma = df['close'].rolling(period).mean()
    sma_indicator = SMA(df, period)
    assert sma.equals(sma_indicator.execute())
    sma_indicator.greater()
    sma_indicator.greater_equal()
    sma_indicator.less()
    sma_indicator.less_equal()
    df['sma'] = sma
    LOGGER.debug(f"{df.iloc[-1]}")


def test_baseAlgoToConf_init():
    indicators = [['SMA', [10], 'greater']]
    algo = BaseAlgorithmToConf(['EURUSD'], DEFAULT_RANGE, indicators)
    with pytest.raises(exc.CurrencyNotListed):
        algo = BaseAlgorithmToConf(['asdasd'], DEFAULT_RANGE, indicators)
    with pytest.raises(exc.IndicatorNotListed):
        algo = BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                                   [['dasdasd', [10], 'greater']])
    with pytest.raises(exc.IndicatorError):
        algo = BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                                   [['SMA', [10], 'asdasd']])
        algo.setup()


def test_baseAlgoToConf_setup():
    indicators = [['SMA', [10], 'greater']]
    algo = BaseAlgorithmToConf(['EURUSD', 'AUDUSD'], DEFAULT_RANGE, indicators)
    algo.setup()


def test_baseAlgoConfigured():
    algo = SimpleAlgorithm001()
    algo.setup()
