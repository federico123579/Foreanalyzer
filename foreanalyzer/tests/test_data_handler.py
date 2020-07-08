"""
tests.test_data_handler
~~~~~~~~~~~~~~~~~~~~~~~

Test the data_handler module.
"""

import logging
import os

import pandas as pd
import pytest

import foreanalyzer._internal_utils as internal
from foreanalyzer.data_handler import CSVDataHandler, XTBDataHandler

LOGGER = logging.getLogger("foreanalyzer.tests.test_data_handler")

OUTER_FOLDER_PATH = os.path.join(internal.OUTER_FOLDER_PATH, 'data')
RANGE_OF_VALUES = 1000
TIMEFRAME = 300
TIME_PAST = 604800


def cleaning():
    """delete extracted csv files"""
    for instr in internal.ACC_CURRENCIES:
        path = os.path.join(
            internal.FOLDER_PATH, 'data', instr + '.csv')
        if os.path.isfile(path):
            os.remove(path)
    LOGGER.debug("cleaning completed...")

@pytest.mark.parametrize("currency", internal.ACC_CURRENCIES)
def test_unzip_data(currency):
    """extract and test again"""
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = internal.unzip_data(
            OUTER_FOLDER_PATH, currency)
    assert not_already_zipped == 0
    cleaning()


@pytest.mark.parametrize("currency", internal.ACC_CURRENCIES)
def test_loadedCSVData_single(currency):
    handle = CSVDataHandler(RANGE_OF_VALUES)
    data = handle.dataframes[currency]
    data.load()
    assert hasattr(handle, 'dataframes')
    assert isinstance(handle.dataframes, dict)
    assert currency in handle.dataframes.keys()
    assert isinstance(data.data, pd.DataFrame)
    assert all([x for x in data.data.columns if x == x.lower()])
    LOGGER.debug(data.data.head())
    cleaning()


@pytest.mark.parametrize("currency", internal.ACC_CURRENCIES)
def test_loadedXTBData_single(currency):
    handle = XTBDataHandler(TIMEFRAME, TIME_PAST)
    data = handle.dataframes[currency]
    data.load()
    assert hasattr(handle, 'dataframes')
    assert isinstance(handle.dataframes, dict)
    assert currency in handle.dataframes.keys()
    assert isinstance(data.data, pd.DataFrame)
    assert all([x for x in data.data.columns if x == x.lower()])
    LOGGER.debug(data.data.head())
    cleaning()


@pytest.mark.parametrize("currency", internal.ACC_CURRENCIES)
def test_loadedData_unload(currency):
    data_handler = CSVDataHandler(RANGE_OF_VALUES)
    handle = data_handler.dataframes[currency]
    handle.load()
    handle.unload()
    for instr in internal.ACC_CURRENCIES:
        assert not data_handler.dataframes[instr].data
    cleaning()
