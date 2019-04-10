"""
foreanalyzer.account
~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

from foreanalyzer import exceptions
from foreanalyzer._internal_utils import CURRENCY, MODE
from foreanalyzer.api_handler import ApiClient


class Trade(object):
    """virtual replacement of trade"""

    def __init__(self, symbol, mode, volume, op_price, trade_id):
        self.symbol = symbol
        self.mode = mode
        self.volume = volume
        self.trade_id = trade_id
        self.op_price = op_price
        self.cl_price = None

    def get_profit(self, cl_price):
        self.cl_price = cl_price
        return ApiClient().api.get_profit_calculation(
            self.symbol.value, self.mode.value, self.volume, self.op_price,
            self.cl_price)['profit']


class Account(object):
    """virtual account"""

    def __init__(self, initial_funds):
        if not isinstance(initial_funds, int):
            raise ValueError("initial funds must be an int")
        self.client = ApiClient()
        self.api = self.client.api
        self.initial_funds = initial_funds
        self.funds = initial_funds
        # for id assignment
        self._trade_count = 0
        self.positions = {}

    def open_trade(self, symbol, mode, volume, op_price):
        """open trade virtually"""
        assert symbol in CURRENCY
        assert mode in MODE
        trade = Trade(symbol, mode, volume, op_price, self._trade_count)
        self.positions[trade.trade_id] = trade
        self._trade_count += 1

    def close_trade(self, trade_id, cl_price):
        """close virtual trade"""
        trade = self.positions[trade_id]
        profit = trade.get_profit(cl_price)
        if self.funds + profit < 0:
            self.funds = 0
            raise exceptions.FundsExhausted()
        else:
            self.funds += profit
        self.positions.pop(trade_id, None)
        return self.funds

#     @property
#     def used_funds(self):
#         """used funds"""
#         if len(self.positions) > 0:
#             return sum(x.used_funds for x in self.positions)
#         else:
#             return 0
#
#     @property
#     def free_funds(self):
#         """free funds"""
#         return self.funds - self.used_funds
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
#         if self.funds + gain < 0:
#             self.funds = 0
#             raise exceptions.FundsExhausted()
#         else:
#             self.funds += gain
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
