"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import logging

import foreanalyzer._internal_utils as internal
import foreanalyzer.algo_modules as mod
from foreanalyzer.account import Account

LOGGER = logging.getLogger("foreanalyzer.engine")


# ============================== ENGINE ==============================
# Engine take the responasibility of combining algo and account in
# a same istances and analyse algos trough a range of processes and
# through various currencies.
# ============================== ENGINE ==============================

class Engine(object):
    """main class controller"""

    def __init__(self):
        config = internal.read_config()['engine']
        algos_name = config['algorithms']
        self.initial_balance = config['initial_balance']
        self.account = Account(self.initial_balance)
        self.algos = [getattr(mod, algo_name) for algo_name in algos_name]

    def setup(self):
        """setup account and algorithm"""
        self.account.setup()
        for algo in self.algos:
            setattr(self, algo.name, algo)
            algo.setup()
