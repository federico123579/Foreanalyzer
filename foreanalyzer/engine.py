"""
foreanalyzer.engine
~~~~~~~~~~~~~~~~~~~~~~~

Main engine for the simulation.
"""

from foreanalyzer._internal_utils import read_config
from foreanalyzer.data_handler import DataHandler
from foreanalyzer.simulation import AccountSimulated

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.engine")

# Engine
class EngineBridge(object):
    """engine"""

    def __init__(self):
        config = read_config()
        # data to feed
        self.handler = DataHandler(config['engine']['range_of_simulation'])
        # init simulation components
        self.account = AccountSimulated()
