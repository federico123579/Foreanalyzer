"""
foreanalyzer.account
~~~~~~~~~~~~~~~~~~~~

Store the simulated Account abstract object.
"""

import os.path

from foreanalyzer import exceptions, tables
from foreanalyzer._internal_utils import (ACC_CURRENCIES, INVERTED_MODE, MODE,
                                          Singleton, read_config)
from forex_python.converter import CurrencyRates
from trading212api.api import Client


class Account(object):
    """abstract account"""

    def __init__(self, margin_mode, initial_funds):
        if not isinstance(initial_funds, int):
            raise ValueError("initial funds must be an int")
        if margin_mode not in ["beginner", "pro"]:
            raise ValueError("margin_mode not recognized")
        self.margin_mode = margin_mode
        self.initial_funds = initial_funds # constant
        self.funds = initial_funds # variable
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
        return self.funds - self.used_funds

    def update_price(self, instrument):
        """update price of price_tables"""
        price = self.api.update_price(instrument.value).price
        self.price_tables[instrument] = price
        return price

    def make_order(self, mode, instrument, quantity):
        """make an order"""
        if instrument not in self.price_tables:
            raise exceptions.PriceNotUpdated()
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
        pos = Position(self, instrument, mode, quantity, margin)
        # WARNING: instrument needs to be in price_tables (need update price otherwise)
        if pos.used_funds > self.free_funds:
            raise exceptions.OrderAborted()
        if instrument not in self.instruments:
            self.instruments.append(instrument)
        self.positions.append(pos)
        return pos

    def close_position(self, position):
        self.funds += position.gain


class Handler(metaclass=Singleton):
    """handler for api use"""

    def __init__(self):
        # set up api
        config = read_config()
        self.api = Client()
        self.api.login(config['account']['username'],
                       config['account']['password'])


class Position(object):
    """position to do"""

    def __init__(self, account, instrument, mode, quantity, margin):
        self.account = account
        self.instrument = instrument
        self.mode = mode
        self.quantity = quantity
        self.open_price = account.price_tables[instrument][INVERTED_MODE[mode.value]]
        self.target_price = account.price_tables[instrument][mode.value]
        self.spread = abs(self.open_price - self.target_price)
        self.margin = margin
        c = CurrencyRates()
        eur_mult = c.get_rate('EUR', instrument.value[:3])
        self.conv_rate = eur_mult * \
            c.get_rate(instrument.value[:3], instrument.value[3:])
        self.used_funds = margin * quantity / \
            self.conv_rate * self.target_price

    @property
    def current_price(self):
        """update price of price_tables"""
        price_couple = self.account.price_tables[self.instrument]
        return price_couple[self.mode.value]

    @property
    def gain(self):
        if self.mode == MODE.BUY:
            pure_gain = self.current_price - self.target_price
        elif self.mode == MODE.SELL:
            pure_gain = self.target_price - self.current_price
        return self.quantity * pure_gain / self.conv_rate

    def close(self):
        self.account.close_position(self)
