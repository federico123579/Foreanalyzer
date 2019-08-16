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
from foreanalyzer.algorithm import BaseAlgorithmToConf, BaseAlgorithmConfigured
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
DEFAULT_CURRENCY = CURRENCY.EURUSD
DEFAULT_RANGE = 1000


@pytest.fixture(scope="module")
def _get_dataframe():
    return DataHandler(1000).dataframes[DEFAULT_CURRENCY].load().copy()


# ============================== TEST INDICATORS ==============================

class TestSMA(object):
    def test_values(self, _get_dataframe):
        period = 10
        timeframe = 60
        df = _get_dataframe
        sma = df['close'].rolling(period).mean()
        sma_indicator = algocomp.SMA(df, period, timeframe)
        assert sma.equals(sma_indicator.execute())
        df['sma'] = sma
        LOGGER.debug(f"{df.iloc[-1]}")

    def test_reindex(self, _get_dataframe):
        df = _get_dataframe
        period = 10
        timeframe = 600
        sma = algocomp.SMA(df, period, timeframe)
        sma.execute()
        sma.reindex_date()
        LOGGER.debug(sma.date_dataframe)


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


# ================================ TEST FILTERS ===============================

filters = [x for x in algocomp.FilterFactory.keys()]


@pytest.fixture(params=filters)
def _get_filter_scope(request):
    yield request.param


def test_filters(_get_dataframe, _get_filter_scope):
    df = _get_dataframe
    filter_scope = _get_filter_scope
    algo_filter = algocomp.Filter(df)
    values = algocomp.SMA(df, 10, 600).execute()
    algo_filter.update(values)
    algo_filter.execute(filter_scope)


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
