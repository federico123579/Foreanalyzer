"""
foreanalyzer.engine
~~~~~~~~~~~~~~~~~~~~~~~

Main engine for the simulation.
"""

from enum import Enum
from foreanalyzer._internal_utils import read_config
from foreanalyzer.algorithm import AlgorithmExample001
from foreanalyzer.simulation import AccountSimulated

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.engine")


class STATUS(Enum):
    INITIED = 0
    FEEDED = 1


# Engine
class EngineBridge(object):
    """engine"""

    def __init__(self):
        config = read_config()
        # init simulation components
        self.account = AccountSimulated()
        # algo feed
        range_of_simulation = config['engine']['range_of_simulation']
        self.algo = AlgorithmExample001(range_of_simulation)
        self.data = self.algo.data
        # set status
        self.status = STATUS.INITIED

    def feed(self):
        """feed algo"""
        # status
        if self.status != STATUS.INITIED:
            LOGGER.warning("Engine alreay feeded")
        self.algo.feed()
        # set status
        self.status = STATUS.FEEDED

    def find_price(self, timestamp):
        pass
