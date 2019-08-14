"""
tests.test_data_handler
~~~~~~~~~~~~~~~~~~

Test the data_handler module.
"""

import logging
import os

import pandas as pd
import pytest

import foreanalyzer._internal_utils as internal
from foreanalyzer.data_handler import DataHandler, ZipFeeder

LOGGER = logging.getLogger("foreanalyzer.tests.test_data_handler")

OUTER_FOLDER_PATH = os.path.join(internal.OUTER_FOLDER_PATH, 'data')
RANGE_OF_VALUES = 1000


def cleaning():
    for instr in internal.CURRENCY:
        path = os.path.join(internal.FOLDER_PATH, 'data', instr.value + '.csv')
        if os.path.isfile(path):
            os.remove(path)
    LOGGER.debug("cleaning completed...")


def test_unzip_data():
    """extract and test again"""
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = internal.unzip_data(OUTER_FOLDER_PATH, 'EURUSD')
    assert not_already_zipped == 0
    cleaning()


@pytest.fixture(scope="function", params=[x for x in internal.CURRENCY])
def get_zip_file(request):
    instr = request.param
    yield instr


def test_ZipFeeder(get_zip_file):
    instr = get_zip_file
    feeder = ZipFeeder(os.path.join(internal.OUTER_FOLDER_PATH, 'data'))
    feeder.normalize_single(instr)
    path = os.path.join(internal.FOLDER_PATH, 'data', instr.value + '.csv')
    assert os.path.isfile(path)
    cleaning()


def test_loadedData_single():
    handle = DataHandler(RANGE_OF_VALUES)
    data = handle.dataframes[internal.CURRENCY.EURUSD]
    data.load()
    assert hasattr(handle, 'dataframes')
    assert isinstance(handle.dataframes, dict)
    assert internal.CURRENCY.EURUSD in handle.dataframes.keys()
    assert isinstance(data.data, pd.DataFrame)
    assert all([x for x in data.data.columns if x == x.lower()])
    LOGGER.debug(data.data.head())
    cleaning()


def test_loadedData_unload():
    data_handler = DataHandler(RANGE_OF_VALUES)
    handle = data_handler.dataframes[internal.CURRENCY.EURUSD]
    handle.load()
    handle.unload()
    for instr in internal.CURRENCY:
        assert not data_handler.dataframes[instr].data
    cleaning()
