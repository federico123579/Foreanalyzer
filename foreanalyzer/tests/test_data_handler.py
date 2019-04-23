"""
tests.test_data_handler
~~~~~~~~~~~~~~~~~~

Test the data_handler module.
"""

import logging
import os

import pandas as pd
import pytest

from foreanalyzer._internal_utils import (CURRENCY, FOLDER_PATH,
                                          OUTER_FOLDER_PATH, unzip_data)
from foreanalyzer.data_handler import DataHandler, ZipFeeder

LOGGER = logging.getLogger("foreanalyzer.tests.test_data_handler")

OUTER_FOLDER_PATH = os.path.join(OUTER_FOLDER_PATH, 'data')
RANGE_OF_VALUES = 10000


def cleaning():
    for instr in CURRENCY:
        path = os.path.join(FOLDER_PATH, 'data', instr.value + '.csv')
        if os.path.isfile(path):
            os.remove(path)
    LOGGER.debug("cleaning completed...")


def test_unzip_data():
    """extract and test again"""
    LOGGER.debug("RUN test_unzip_data")
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = unzip_data(OUTER_FOLDER_PATH, 'EURUSD')
    assert not_already_zipped == 0
    LOGGER.debug("PASSED test_unzip_data")
    cleaning()


@pytest.fixture(scope="function", params=[x for x in CURRENCY])
def get_zip_file(request):
    instr = request.param
    LOGGER.debug("passing {}".format(instr))
    yield instr


def test_ZipFeeder(get_zip_file):
    instr = get_zip_file
    LOGGER.debug("RUN test_ZipFeeder for {}".format(instr.value))
    feeder = ZipFeeder(OUTER_FOLDER_PATH)
    feeder.normalize_single(instr)
    path = os.path.join(FOLDER_PATH, 'data', instr.value + '.csv')
    assert os.path.isfile(path)
    LOGGER.debug("PASSED test_ZipFeeder for {}".format(instr.value))
    cleaning()


def test_loadedData_single():
    LOGGER.debug("RUN test_loadedData_single")
    handle = DataHandler(RANGE_OF_VALUES)
    data = handle.dataframes[CURRENCY.EURUSD]
    data.load()
    assert hasattr(handle, 'dataframes')
    assert isinstance(handle.dataframes, dict)
    assert CURRENCY.EURUSD in handle.dataframes.keys()
    assert isinstance(data.data, pd.DataFrame)
    assert all([x for x in data.data.columns if x == x.lower()])
    LOGGER.debug(data.data.head())
    LOGGER.debug("PASSED test_loadedData_single")
    cleaning()


def test_loadedData_unload():
    LOGGER.debug("RUN test_loadedData_unload")
    data_handler = DataHandler(RANGE_OF_VALUES)
    handle = data_handler.dataframes[CURRENCY.EURUSD]
    handle.load()
    handle.unload()
    for instr in CURRENCY:
        assert not data_handler.dataframes[instr].data
    LOGGER.debug("PASSED test_loadedData_unload")
    cleaning()
