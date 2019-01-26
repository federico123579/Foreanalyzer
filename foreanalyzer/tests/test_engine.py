"""
tests.test_engine
~~~~~~~~~~~~~~~~~~

Test the engine module.
"""

import pytest
from foreanalyzer.engine import EngineBridge

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_engine")
LOGGER.info("TESTING test_engine.py module")


@pytest.fixture(scope="module")
def get_engine():
    """get engine once"""
    engine = EngineBridge()
    return engine


def test_feed(get_engine):
    """test feed engine"""
    LOGGER.debug("RUN test_feed")
    engine = get_engine
    engine.feed()
    LOGGER.debug("PASSED test_feed")
