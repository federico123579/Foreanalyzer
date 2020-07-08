"""
foreanalyzer.account
~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

from tqdm import tqdm

from foreanalyzer import exceptions
import foreanalyzer._internal_utils as internal
from foreanalyzer.cli import CliConsole
from foreanalyzer.api_handler import ApiClient

LOGGER = CliConsole()
LOGGER.prefix = 'account'


class Trade(object):
    """virtual replacement of trade"""

    def __init__(self, symbol, mode, volume, op_price, trade_id):
        self.symbol = symbol
        self.mode = mode
        self.volume = volume
        self.trade_id = trade_id
        self.op_price = op_price
        self.cl_price = None
        self.profit = None
        self.state = internal.STATE.OPEN
        LOGGER.debug(f"inited Trade #{self.trade_id}")

    def get_profit(self, _mode=1):
        """calculate profit according to api
        0: real - 1: simulated
        simulated set only for EURUSD"""
        if _mode:
            if self.mode.value == 0:
                profit = ((self.cl_price - self.op_price - 0.00009) *
                          self.volume * 100000)
            if self.mode.value == 1:
                profit = ((self.op_price - self.cl_price - 0.00009) *
        else:
            profit = ApiClient().api.get_profit_calculation(
                self.symbol.value, self.mode.value, self.volume,
                self.op_price, self.cl_price)['profit']
                         self.volume * 100000)
        self.profit = profit
        self.state = internal.STATE.EVALUATED
        LOGGER.debug(f"{profit}€ profit got")
        return profit

    def close(self, cl_price):
        """set state closed for remotion from to_evaluate list"""
        self.cl_price = cl_price
        self.state = internal.STATE.CLOSED


class Account(internal.StatusComponent):
    """virtual account"""

    def __init__(self):
        config = internal.read_config()['account']
        self.client = ApiClient()
        self.api = self.client.api
        # account data
        self.initial_balance = config['initial_balance']
        self.balance = config['initial_balance']
        self._count_margin = config['count_margin']
        self._sim_profit = config['simulate_profit']
        self.margin = 0
        self.positions = {}  # for open trades
        self.trades = []  # for closed trades waiting to be evaluated
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
        assert symbol in internal.ACC_CURRENCIES
        assert mode in internal.MODE
        trade = Trade(symbol, mode, volume, op_price, self._trade_count)
        if self._count_margin:
            margin = self.api.get_margin_trade(symbol.value, volume)['margin']
            self.margin += margin
        self.positions[trade.trade_id] = trade
        self._trade_count += 1
        LOGGER.info(f"trade of {volume} {symbol} #{trade.trade_id} opened")
        return trade

    def close_trade(self, trade_id, cl_price):
        """close virtual trade"""
        self._check_status()
        trade = self.positions[trade_id]
        trade.close(cl_price)
        self.positions.pop(trade_id, None)
        self.trades.append(trade)
        LOGGER.info(f"trade #{trade.trade_id} closed")

    def evaluate_trades(self):
        """close effectively all trades"""
        trade_n = 0
        tot_trades_n = len(self.trades)
        with tqdm(total=tot_trades_n) as pbar:
            for trade in self.trades:
                profit = trade.get_profit(self._sim_profit)
                if self.balance + profit < 0:
                    self.balance = 0
                    raise exceptions.FundsExhausted()
                else:
                    self.balance += profit
                    trade.new_balance = self.balance
                    trade_n += 1
                pbar.update(trade_n)
        n_tot_trades = len(self.trades)
        trades_to_del = [t for t in self.trades if t.state ==
                         internal.STATE.EVALUATED]
        trades_evaluated = [trade for trade in self.trades if trade.state ==
                            internal.STATE.EVALUATED]
        # TODO: stabilize this sentence
        _ = [x for x in map(self.trades.remove, trades_to_del)]
        LOGGER.debug(f"{n_tot_trades - len(self.trades)} trades evaluated")
        return trades_evaluated
