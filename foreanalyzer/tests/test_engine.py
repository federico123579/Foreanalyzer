"""
tests.test_engine
~~~~~~~~~~~~~~~~~~

Test the engine module.
"""

import os
import os.path

from foreanalyzer._internal_utils import FOLDER_PATH, unzip_data

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_engine")
LOGGER.info("TESTING test_engine.py module")


def test_unzip_data():
    """extract and test again"""
    LOGGER.debug("RUN test_unzip_data")
    not_already_zipped = 1
    while not_already_zipped:
        not_already_zipped = unzip_data('EURUSD')
    assert not_already_zipped == 0
    LOGGER.debug("PASSED test_unzip_data")
    os.remove(os.path.join(FOLDER_PATH, 'data', 'EURUSD.txt'))
    LOGGER.debug("clean up completed...")
