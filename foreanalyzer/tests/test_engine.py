"""
tests.test_engine
~~~~~~~~~~~~~~~~~~

Test the engine module.
"""

import os
import os.path

from foreanalyzer.engine import ZipFeeder
from foreanalyzer._internal_utils import (ACC_CURRENCIES, FOLDER_PATH,
                                          OUTER_FOLDER_PATH, unzip_data)

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_engine")
LOGGER.info("TESTING test_engine.py module")

OUTER_FOLDER_PATH = os.path.join(OUTER_FOLDER_PATH, 'data')


def test_unzip_data():
    """extract and test again"""
    LOGGER.debug("RUN test_unzip_data")
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = unzip_data(OUTER_FOLDER_PATH, 'EURUSD')
    assert not_already_zipped == 0
    LOGGER.debug("PASSED test_unzip_data")
    os.remove(os.path.join(FOLDER_PATH, 'data', 'EURUSD.txt'))
    LOGGER.debug("clean up completed...")


def test_ZipFeeder():
    LOGGER.debug("RUN test_ZipFeeder")
    feeder = ZipFeeder(OUTER_FOLDER_PATH)
    feeder.normalize_data()
    for instr in ACC_CURRENCIES:
        assert os.path.isfile(os.path.join(
            FOLDER_PATH, 'data', instr.value + '.txt'))
    LOGGER.debug("PASSED test_ZipFeeder")
    for instr in ACC_CURRENCIES:
        os.remove(os.path.join(FOLDER_PATH, 'data', instr.value + '.txt'))
    LOGGER.debug("clean up completed...")
