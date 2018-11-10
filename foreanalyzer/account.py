"""
foreanalyzer.account
~~~~~~~~~~~~~~~~~~~~

Store the simulated Account abstract object.
"""

import os.path
from configparser import ConfigParser

from foreanalyzer import tables
from foreanalyzer._internal_utils import (ACC_CURRENCIES, INVERTED_MODE, MODE,
                                          Singleton)
from forex_python.converter import CurrencyRates
from trading212api.api import Client


class Handler(metaclass=Singleton):
    def __init__(self):
        # set up api
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'config.ini'))
        self.api = Client()
        self.api.login(config['ACCOUNT']['username'],
                       config['ACCOUNT']['password'])


class Account(object):
    """abstract account"""

    def __init__(self, margin_mode, initial_funds):
        if margin_mode not in ["beginner", "pro"]:
            raise ValueError("margin_mode not recognized")
        self.margin_mode = margin_mode
        self.initial_funds = initial_funds
        self.positions = []
        self.instruments = []
        # tables of prices for instruments
        self.price_tables = {}
        self.api = Handler().api

    @property
    def used_funds(self):
        """used funds"""
        if len(self.positions) > 0:
            return sum(x.used_funds for x in self.positions)
        else:
            return 0
    
    @property
    def free_funds(self):
        """free funds"""
        return self.initial_funds - self.used_funds

    def update_price(self, instrument):
        """update price of price_tables"""
        price = self.api.update_price(instrument.value).price
        self.price_tables[instrument] = price
        return price

    def make_order(self, mode, instrument, quantity):
        """make an order"""
        if mode not in MODE:
            raise ValueError("{} nor buy or sell".format(mode))
        if instrument not in ACC_CURRENCIES:
            raise ValueError("{} not valid".format(instrument))
        if quantity < tables.CURRENCIES[instrument.value].min_quantity:
            quantity = 0
        if self.margin_mode == 'beginner':
            margin = tables.CURRENCIES[instrument.value].stnd_margin
        elif self.margin_mode == 'pro':
            margin = tables.CURRENCIES[instrument.value].pro_margin
        # ...
        # WARNING: instrument needs to be in price_tables (need update price otherwise)
        pos = Position(instrument, mode, quantity,
                       self.price_tables[instrument], margin)
        if instrument not in self.instruments:
            self.instruments.append(instrument)
        self.positions.append(pos)
        return pos


class Position(object):
    """position to do"""

    def __init__(self, instrument, mode, quantity, price_couple, margin):
        self.instrument = instrument
        self.mode = mode
        self.quantity = quantity
        self.open_price = price_couple[INVERTED_MODE[mode.value]]
        self.target_price = price_couple[mode.value]
        self.spread = abs(self.open_price - self.target_price)
        self.margin = margin
        c = CurrencyRates()
        eur_mult = c.get_rate('EUR', instrument.value[:3])
        rate = eur_mult * c.get_rate(instrument.value[:3], instrument.value[3:])
        self.used_funds = margin * quantity * \
            rate * price_couple[mode.value]
