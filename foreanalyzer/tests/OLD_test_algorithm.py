"""
test.test_algorithm
~~~~~~~~~~~~~~~~~

Test base algorithm and algo components.
"""

import logging

import pandas as pd
import pytest

import foreanalyzer.algo_components as algocomp
import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import CURRENCY, STATUS
from foreanalyzer.algorithm import BaseAlgorithmToConf, BaseAlgorithmConfigured
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
DEFAULT_CURRENCY = CURRENCY.EURUSD
DEFAULT_RANGE = 1000


@pytest.fixture(scope="module")
def _get_dataframe():
    return DataHandler(DEFAULT_RANGE).dataframes[DEFAULT_CURRENCY].load().copy()


# ============================== TEST INDICATORS ==============================

SMA_PERIOD = 12
SMA_TIMEFRAME = 1800

class TestSMA(object):
    def test_values(self, _get_dataframe):
        """testing with minimum frequency"""
        period = SMA_PERIOD
        timeframe = 60
        df = _get_dataframe
        sma = df['close'].rolling(period).mean()
        sma_indicator = algocomp.SMA(df, period, timeframe)
        assert sma.equals(sma_indicator.submit())
        df['sma'] = sma
        LOGGER.debug(f"{df.iloc[-1]}")

    # TODO: add test reduce

    def test_reindex(self, _get_dataframe):
        df = _get_dataframe
        period = SMA_PERIOD
        timeframe = SMA_TIMEFRAME
        sma = algocomp.SMA(df, period, timeframe)
        sma.submit()
        sma.reindex_date()
        LOGGER.debug(sma.dataframe_reindexed)


# =============================== TEST REDUCERS ===============================

periods = [60, 120, 600, 3600]


@pytest.fixture(params=periods)
def _get_period(request):
    yield request.param


# noinspection PyTypeChecker
def test_PeriodReducer(_get_period, _get_dataframe):
    df = _get_dataframe
    period = _get_period
    trigger = algocomp.PeriodReducer(df, period)
    trigger.execute()
    assert all(trigger.dataframe.reset_index()[
                   'datetime'].diff().dropna().dt.seconds >= period)


# ============================== TEST ALGORITHMS ==============================

def test_baseAlgoToConf_init():
    indicators = [['SMA', [10, 600], 'above']]
    BaseAlgorithmToConf(['EURUSD'], DEFAULT_RANGE, indicators)
    # test parameters
    with pytest.raises(exc.CurrencyNotListed):
        BaseAlgorithmToConf(['test'], DEFAULT_RANGE, indicators)
    with pytest.raises(exc.IndicatorNotListed):
        BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                            [['test', [10, 600], 'above']])
    with pytest.raises(exc.IndicatorError):
        algo = BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                                   [['SMA', [10, 600], 'test']])
        algo.setup()


def test_baseAlgoToConf_setup():
    indicators = [['SMA', [10, 600], 'above']]
    algo = BaseAlgorithmToConf(['EURUSD', 'AUDUSD'], DEFAULT_RANGE, indicators)
    # test methods
    with pytest.raises(exc.AlgorithmNotExecuted):
        algo.get_datetime_trades(DEFAULT_CURRENCY)
    # test post-setup
    algo.setup()
    for currency in algo.currencies:
        df = algo.dataframes[currency]
        assert hasattr(df, 'SMA')
        assert df.SMA.status == STATUS.EXECUTED
        assert df.SMA.reducer.status == STATUS.EXECUTED


def test_get_datetime_trades():
    indicators = [['SMA', [10, 600], 'above']]
    algo = BaseAlgorithmToConf(['EURUSD'], DEFAULT_RANGE, indicators)
    algo.setup()
    dates = algo.get_datetime_trades(CURRENCY.EURUSD)
    LOGGER.debug(dates)


def test_baseAlgoConfigured():
    algo = BaseAlgorithmConfigured('SimpleAlgorithm001')
    algo.setup()
