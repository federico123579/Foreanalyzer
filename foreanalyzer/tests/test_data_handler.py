"""
tests.test_data_handler
~~~~~~~~~~~~~~~~~~

Test the data_handler module.
"""

import os
import pytest

import pandas as pd

from foreanalyzer._internal_utils import (ACC_CURRENCIES, FOLDER_PATH,
                                          OUTER_FOLDER_PATH, unzip_data)
from foreanalyzer.data_handler import DataHandler, ZipFeeder

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_data_handler")
LOGGER.info("TESTING test_data_handler.py module")

OUTER_FOLDER_PATH = os.path.join(OUTER_FOLDER_PATH, 'data')
RANGE_OF_VALUES = 10000


def cleaning():
    for instr in ACC_CURRENCIES:
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


@pytest.fixture(scope="function", params=[x for x in ACC_CURRENCIES])
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
    data = handle.load_data(ACC_CURRENCIES.EURUSD)
    assert hasattr(handle, 'data')
    assert isinstance(handle.data, dict)
    assert 'EURUSD' in handle.data.keys()
    assert isinstance(data, pd.DataFrame)
    assert all([x for x in data.columns if x == x.lower()])
    LOGGER.debug(data.head())
    LOGGER.debug("PASSED test_loadedData_single")
    cleaning()

def test_loadedData_all():
    LOGGER.debug("RUN test_loadedData_all")
    handle = DataHandler(RANGE_OF_VALUES)
    data = handle.get_data()
    for instr in ACC_CURRENCIES:
        expected_dataframe = data[instr.value]
        assert isinstance(expected_dataframe, pd.DataFrame)
        assert all([x for x in expected_dataframe.columns if x == x.lower()])
    LOGGER.debug("PASSED test_loadedData_all")
    cleaning()

def test_loadedData_unload():
    LOGGER.debug("RUN test_loadedData_unload")
    handle = DataHandler(RANGE_OF_VALUES)
    data = handle.load_data(ACC_CURRENCIES.EURUSD)
    handle.unload_data()
    for instr in ACC_CURRENCIES: 
        assert instr.value not in handle.data.keys()
    LOGGER.debug("PASSED test_loadedData_unload")
    cleaning()
