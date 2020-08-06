"""
test.test_boll_bands_1
~~~~~~~~~~~~~~~~~~~~~~

Test the Boll Bands 1 algo module.
"""

import logging

from foreanalyzer.algo_modules.boll_bands_1 import BolligerBands1

LOGGER = logging.getLogger("foreanalyzer.tests.test_boll_bands_1")


def test_algo_setup():
    algo = BolligerBands1()

