"""
foreanalyzer.engine
~~~~~~~~~~~~~~~~~~~~~~~

Main engine for the simulation.
"""

from foreanalyzer._internal_utils import (ACC_CURRENCIES, OUTER_FOLDER_PATH,
                                          unzip_data)
from foreanalyzer.data_handler import DataHandler
from foreanalyzer.simulation import AccountSimulated

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.engine")


class EngineBridge(object):
    """engine"""

    def __init__(self):
        # data to feed
        self.handler = DataHandler()
        # init simulation components
        self.account = AccountSimulated()
