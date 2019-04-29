"""
test.test_algorithm
~~~~~~~~~~~~~~~~~

Test algos.
"""

import logging

import pytest

import foreanalyzer.algo_components as algocomp
import foreanalyzer.exceptions as exc
from foreanalyzer._internal_utils import CURRENCY, STATUS
from foreanalyzer.algorithm import BaseAlgorithmToConf, SimpleAlgorithm001
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
DEFAULT_CURRENCY = CURRENCY.EURUSD
DEFAULT_RANGE = 1000


@pytest.fixture(scope="module")
def _get_dataframe():
    return DataHandler(1000).dataframes[DEFAULT_CURRENCY].load().copy()


# ============================== TEST INDICATORS ==============================


def test_SMA(_get_dataframe):
    period = 10
    timeframe = 60
    df = _get_dataframe
    sma = df['close'].rolling(period).mean()
    sma_indicator = algocomp.SMA(df, period, timeframe)
    assert sma.equals(sma_indicator.execute())
    sma_indicator.above()
    sma_indicator.above_equal()
    sma_indicator.below()
    sma_indicator.below_equal()
    df['sma'] = sma
    LOGGER.debug(f"{df.iloc[-1]}")


# =============================== TEST TRIGGERS ===============================

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
    assert all(trigger.dataframe['timestamp'].diff().dropna().dt.seconds >=
               period)


# ============================== TEST ALGORITHMS ==============================

def test_baseAlgoToConf_init():
    indicators = [['SMA', [10, 600], 'above']]
    BaseAlgorithmToConf(['EURUSD'], DEFAULT_RANGE, indicators)
    with pytest.raises(exc.CurrencyNotListed):
        BaseAlgorithmToConf(['test'], DEFAULT_RANGE, indicators)
    # test error with name of instruments
    with pytest.raises(exc.IndicatorNotListed):
        BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                            [['test', [10, 600], 'above']])
    # with pytest.raises(exc.TriggerNotListed):
    #     BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
    #                         indicators, ['test', [10]])
    # test error with scope
    with pytest.raises(exc.IndicatorError):
        algo = BaseAlgorithmToConf([DEFAULT_CURRENCY], DEFAULT_RANGE,
                                   [['SMA', [10, 600], 'test']])
        algo.setup()


def test_baseAlgoToConf_setup():
    indicators = [['SMA', [10, 600], 'above']]
    algo = BaseAlgorithmToConf(['EURUSD', 'AUDUSD'], DEFAULT_RANGE, indicators)
    algo.setup()
    for currency in algo.currencies:
        df = algo.dataframes[currency]
        assert hasattr(df, 'SMA')
        assert df.SMA.status == STATUS.EXECUTED
        assert df.SMA.reducer.status == STATUS.EXECUTED


def test_baseAlgoConfigured():
    algo = SimpleAlgorithm001()
    algo.setup()
