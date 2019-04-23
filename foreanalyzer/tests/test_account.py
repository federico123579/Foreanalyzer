"""
test.test_account
~~~~~~~~~~~~~~~~~

Test account.
"""

import logging
import time

import pytest

from foreanalyzer._internal_utils import CURRENCY, MODE, STATE
from foreanalyzer.account import Account
from foreanalyzer.exceptions import FundsExhausted

LOGGER = logging.getLogger("foreanalyzer.tests.test_account")
DEFAULT_ACCOUNT_BALANCE = 1000
DEFAULT_SYMBOL = CURRENCY.EURUSD
DEFAULT_MODE = MODE.buy
DEFAULT_VOLUME = 0.5
DEFAULT_OP_PRICE = 1.40
DEFAULT_CL_PRICE = 1.41
DEFAULT_CL_PRICE_BALANCE_EXHAUSTED = 0.41
DEFAULT_TRADES_TO_EVALUATE = 10


@pytest.fixture(scope="function")
def get_account():
    account = Account(DEFAULT_ACCOUNT_BALANCE)
    account.setup()
    return account


@pytest.fixture(scope="function")
def setup_and_trade():
    account = Account(DEFAULT_ACCOUNT_BALANCE)
    account.setup()
    trade = account.open_trade(DEFAULT_SYMBOL, DEFAULT_MODE, DEFAULT_VOLUME,
                               DEFAULT_OP_PRICE)
    return account, trade


def test_open_trade(get_account):
    account = get_account
    trade = account.open_trade(DEFAULT_SYMBOL, DEFAULT_MODE, DEFAULT_VOLUME,
                               DEFAULT_OP_PRICE)
    assert trade == account.positions.get(trade.trade_id)
    assert trade.symbol == DEFAULT_SYMBOL
    assert trade.mode == DEFAULT_MODE
    assert trade.volume == DEFAULT_VOLUME
    assert trade.op_price == DEFAULT_OP_PRICE
    LOGGER.debug("passed test_open_trade")


def test_close_trade(setup_and_trade):
    account, trade = setup_and_trade
    account.close_trade(trade.trade_id, DEFAULT_CL_PRICE)
    assert trade.state == STATE.CLOSED
    # assert profit == trade.get_profit(DEFAULT_CL_PRICE)
    # assert account.balance == DEFAULT_ACCOUNT_BALANCE + profit
    LOGGER.debug("passed test_get_profit")


def test_get_profit(setup_and_trade):
    account, trade = setup_and_trade
    trade.close(DEFAULT_CL_PRICE)
    profit = trade.get_profit()
    assert profit >= 0
    theoretical_profit = account.api.get_profit_calculation(
        DEFAULT_SYMBOL.value, DEFAULT_MODE.value, DEFAULT_VOLUME,
        DEFAULT_OP_PRICE, DEFAULT_CL_PRICE)['profit']
    assert theoretical_profit == profit
    LOGGER.debug("passed test_get_profit")


def test_evaluate_trades(get_account):
    account = get_account
    account.setup()
    # open and close five test trades
    start = time.time()
    for _ in range(DEFAULT_TRADES_TO_EVALUATE):
        trade = account.open_trade(DEFAULT_SYMBOL, DEFAULT_MODE,
                                   DEFAULT_VOLUME, DEFAULT_OP_PRICE)
        account.close_trade(trade.trade_id, DEFAULT_CL_PRICE)
    end = time.time()
    LOGGER.debug(f"opened {DEFAULT_TRADES_TO_EVALUATE} trades in "
                 f"{end - start} sec")
    # evaluate
    LOGGER.debug("evaluating...")
    start = time.time()
    account.evaluate_trades()
    end = time.time()
    LOGGER.debug(f"evaluated trades in {end - start}")


def test_balance_exhausted(get_account):
    account = get_account
    with pytest.raises(FundsExhausted):
        trade = account.open_trade(
            DEFAULT_SYMBOL, DEFAULT_MODE, DEFAULT_VOLUME, DEFAULT_OP_PRICE)
        account.close_trade(trade.trade_id, DEFAULT_CL_PRICE_BALANCE_EXHAUSTED)
        account.evaluate_trades()
    assert account.balance == 0
    LOGGER.debug("passed test_balance_exhausted")
