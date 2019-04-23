"""
test.test_algorithm
~~~~~~~~~~~~~~~~~

Test algos.
"""

import logging

from foreanalyzer._internal_utils import CURRENCY
from foreanalyzer.algorithm import SMA
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
DEFAULT_CURRENCY = CURRENCY.EURUSD


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
