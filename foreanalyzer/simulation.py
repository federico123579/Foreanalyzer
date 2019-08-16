"""
foreanalyzer.simulation
~~~~~~~~~~~~~~~~~~~~~~~

Store the simulation objects.
"""

from foreanalyzer._internal_utils import ACC_CURRENCIES, read_config
from foreanalyzer.account import Account

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.simulation")


class AccountSimulated(Account):
    """simulation of account"""

    def __init__(self):
        self.config = read_config()
        margin_mode = self.config['simulation']['margin_mode']
        initial_funds = self.config['simulation']['initial_funds']
        super().__init__(margin_mode, initial_funds)

    def simulate(self, instrument, buy_ask_price, sell_bid_price):
        """update price_couple in account"""
        if instrument not in ACC_CURRENCIES:
            raise ValueError("Instrument not accepted")
        if instrument not in self.price_tables:
            self.price_tables[instrument] = {}
        self.price_tables[instrument]['buy'] = buy_ask_price
        self.price_tables[instrument]['sell'] = sell_bid_price
