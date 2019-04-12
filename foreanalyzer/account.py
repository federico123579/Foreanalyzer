"""
foreanalyzer.account
~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

import logging

import foreanalyzer._internal_utils as internal
from foreanalyzer import exceptions
from foreanalyzer.api_handler import ApiClient

LOGGER = logging.getLogger("foreanalyzer.account")


class Trade(object):
    """virtual replacement of trade"""

    def __init__(self, symbol, mode, volume, op_price, trade_id):
        self.symbol = symbol
        self.mode = mode
        self.volume = volume
        self.trade_id = trade_id
        self.op_price = op_price
        self.cl_price = None
        self.state = internal.STATE.OPEN
        LOGGER.debug(f"inited Trade #{self.trade_id}")

    def get_profit(self, cl_price):
        self.cl_price = cl_price
        profit = ApiClient().api.get_profit_calculation(
            self.symbol.value, self.mode.value, self.volume, self.op_price,
            self.cl_price)['profit']
        LOGGER.debug(f"{profit}€ profit got")
        return profit

    def close(self, cl_price):
        profit = self.get_profit(cl_price)
        self.state = internal.STATE.CLOSED
        LOGGER.debug(f"trade #{self.trade_id} closed")
        return profit


class Account(internal.StatusComponent):
    """virtual account"""

    def __init__(self, initial_balance):
        if not isinstance(initial_balance, int):
            raise ValueError("initial balance must be an int")
        self.client = ApiClient()
        self.api = self.client.api
        # account data
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}
        # for id assignment
        self._trade_count = 0
        super().__init__()
        LOGGER.debug("Account inited")

    def setup(self):
        """start api handler"""
        self.client.setup()
        super().setup()

    def shutdown(self):
        """stop api handler"""
        self.client.shutdown()
        super().shutdown()

    def _check_status(self):
        """check if set up"""
        if self.status == internal.STATUS.OFF:
            raise exceptions.NotLogged()
        else:
            pass

    def open_trade(self, symbol, mode, volume, op_price):
        """open trade virtually"""
        self._check_status()
        assert symbol in internal.CURRENCY
        assert mode in internal.MODE
        trade = Trade(symbol, mode, volume, op_price, self._trade_count)
        self.positions[trade.trade_id] = trade
        self._trade_count += 1
        LOGGER.info(f"trade of {volume} {symbol} #{trade.trade_id} opened")
        return trade

    def close_trade(self, trade_id, cl_price):
        """close virtual trade"""
        self._check_status()
        trade = self.positions[trade_id]
        profit = trade.close(cl_price)
        if self.balance + profit < 0:
            self.balance = 0
            raise exceptions.FundsExhausted()
        else:
            self.balance += profit
        self.positions.pop(trade_id, None)
        LOGGER.info(f"trade #{trade.trade_id} closed with profit {profit}€")
        return profit

#     @property
#     def used_funds(self):
#         """used balance"""
#         if len(self.positions) > 0:
#             return sum(x.used_funds for x in self.positions)
#         else:
#             return 0
#
#     @property
#     def free_funds(self):
#         """free balance"""
#         return self.balance - self.used_funds
#
#     def update_price(self, instrument):
#         """update price of price_tables"""
#         price = self.api.update_price(instrument.value).price
#         self.price_tables[instrument] = price
#         return price
#
#     def make_order(self, mode, instrument, quantity):
#         """make an order"""
#         if instrument not in self.price_tables:
#             raise exceptions.PriceNotUpdated()
#         if mode not in MODE:
#             raise ValueError("{} nor buy or sell".format(mode))
#         if instrument not in CURRENCY:
#             raise ValueError("{} not valid".format(instrument))
#         if quantity < tables.CURRENCY[instrument.value].min_quantity:
#             quantity = 0
#         if self.margin_mode == 'beginner':
#             margin = tables.CURRENCY[instrument.value].stnd_margin
#         elif self.margin_mode == 'pro':
#             margin = tables.CURRENCY[instrument.value].pro_margin
#         pos = Position(self, instrument, mode, quantity, margin)
#         # WARNING: instrument needs to be in price_tables (need update price
#         # otherwise)
#         if pos.used_funds > self.free_funds:
#             raise exceptions.OrderAborted()
#         if instrument not in self.instruments:
#             self.instruments.append(instrument)
#         self.positions.append(pos)
#         return pos
#
#     def close_position(self, position):
#         gain = position.gain
#         if self.balance + gain < 0:
#             self.balance = 0
#             raise exceptions.FundsExhausted()
#         else:
#             self.balance += gain
#
#
# class Handler(metaclass=Singleton):
#     """handler for api use"""
#
#     def __init__(self):
#         # set up api
#         config = read_config()
#         self.api = Client()
#         self.api.login(config['account']['username'],
#                        config['account']['password'])
#
#
# class Position(object):
#     """position to do"""
#
#     def __init__(self, account, instrument, mode, quantity, margin):
#         self.account = account
#         self.instrument = instrument
#         self.mode = mode
#         self.quantity = quantity
#         self.open_price = account.price_tables[instrument][INVERTED_MODE[mode.value]]
#         self.target_price = account.price_tables[instrument][mode.value]
#         self.spread = abs(self.open_price - self.target_price)
#         self.margin = margin
#         c = CurrencyRates()
#         eur_mult = c.get_rate('EUR', instrument.value[:3])
#         self.conv_rate = eur_mult * \
#             c.get_rate(instrument.value[:3], instrument.value[3:])
#         self.used_funds = margin * quantity / \
#             self.conv_rate * self.target_price
#
#     @property
#     def current_price(self):
#         """update price of price_tables"""
#         price_couple = self.account.price_tables[self.instrument]
#         return price_couple[self.mode.value]
#
#     @property
#     def gain(self):
#         """give the result"""
#         if self.mode == MODE.BUY:
#             pure_gain = self.current_price - self.target_price
#         elif self.mode == MODE.SELL:
#             pure_gain = self.target_price - self.current_price
#         return self.quantity * pure_gain / self.conv_rate
#
#     def close(self):
#         self.account.close_position(self)
