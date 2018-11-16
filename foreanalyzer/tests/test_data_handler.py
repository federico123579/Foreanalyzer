"""
tests.test_data_handler
~~~~~~~~~~~~~~~~~~

Test the data_handler module.
"""

import os

import pytest
from foreanalyzer._internal_utils import (ACC_CURRENCIES, FOLDER_PATH,
                                          OUTER_FOLDER_PATH, unzip_data)
from foreanalyzer.data_handler import DataHandler, ZipFeeder

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_data_handler")
LOGGER.info("TESTING test_data_handler.py module")

OUTER_FOLDER_PATH = os.path.join(OUTER_FOLDER_PATH, 'data')


def test_unzip_data():
    """extract and test again"""
    LOGGER.debug("RUN test_unzip_data")
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = unzip_data(OUTER_FOLDER_PATH, 'EURUSD')
    assert not_already_zipped == 0
    LOGGER.debug("PASSED test_unzip_data")
    os.remove(os.path.join(FOLDER_PATH, 'data', 'EURUSD.csv'))
    LOGGER.debug("clean up completed...")


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
    os.remove(path)
    LOGGER.debug("clean up completed...")
