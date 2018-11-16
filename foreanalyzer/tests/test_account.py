"""
test.test_account
~~~~~~~~~~~~~~~~~

Test account.
"""

import time
import pytest
from foreanalyzer._internal_utils import ACC_CURRENCIES, MODE
from foreanalyzer.account import Account, Position
from foreanalyzer.exceptions import FundsExhausted, OrderAborted
from foreanalyzer.tables import CURRENCIES

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_account")
LOGGER.info("TESTING test_account.py module")


@pytest.fixture(scope="function", params=["beginner", "pro"])
def get_account(request):
    param = request.param
    yield Account(param, 1000)


orders = []
orders_1 = [[MODE.BUY, x, 5000] for x in ACC_CURRENCIES]
orders_2 = [[MODE.BUY, x, 1] for x in ACC_CURRENCIES]
orders.extend(orders_1)
orders.extend(orders_2)


@pytest.fixture(scope="function", params=orders)
def get_lot_orders(request):
    param = request.param
    yield param


def test_make_order(get_account, get_lot_orders):
    """test the big function of make order"""
    LOGGER.debug("RUN test_make_order")
    # PARAMS
    acc = get_account
    param = get_lot_orders
    # make order
    acc.update_price(param[1])
    order = acc.make_order(param[0], param[1], param[2])
    # order in list of positions
    assert order in acc.positions
    # name in instruments used
    assert param[1] == order.instrument
    assert param[1] in acc.instruments
    # spread applied
    assert hasattr(order, 'spread')
    # quantity respected
    assert (order.quantity >= CURRENCIES[param[1].value].min_quantity
            or order.quantity == 0)
    # margin applied based on margin_mode
    if acc.margin_mode == 'beginner':
        assert order.margin == CURRENCIES[param[1].value].stnd_margin
    elif acc.margin_mode == 'pro':
        assert order.margin == CURRENCIES[param[1].value].pro_margin
    # funds used updated
    LOGGER.debug("RESULT test_used_funds - {}".format(order.used_funds))
    assert acc.used_funds == order.used_funds
    # funds free updated
    assert acc.free_funds == acc.initial_funds - acc.used_funds
    # position gain
    acc.update_price(param[1])
    if order.mode == MODE.BUY:
        pure_gain = acc.price_tables[param[1]]['buy'] - order.target_price
    elif order.mode == MODE.SELL:
        pure_gain = order.target_price - acc.price_tables[param[1]]['sell']
    assert order.gain == order.quantity * pure_gain / order.conv_rate
    LOGGER.debug("RESULT test_gain - {}".format(order.gain))
    LOGGER.debug("PASSED test_make_order of {}".format(param[1]))


def test_funds_overcharge(get_account):
    """test the funds if the order is too big"""
    LOGGER.debug("RUN test_funds_overcharge")
    # PARAM
    acc = get_account
    # make order
    acc.update_price(ACC_CURRENCIES.USDJPY)
    # raise
    with pytest.raises(OrderAborted):
        acc.make_order(MODE.BUY, ACC_CURRENCIES.USDJPY, 5000000)
    LOGGER.debug("PASSED test_funds_overcharge")


def test_funds_exhausted():
    """test if raise exception on funds exhausted"""
    LOGGER.debug("RUN test_funds_exhausted")
    acc = Account('beginner', 200)
    EURUSD = ACC_CURRENCIES.EURUSD
    acc.update_price(EURUSD)
    acc.make_order(MODE.BUY, EURUSD, 5000)
    acc.price_tables[ACC_CURRENCIES.EURUSD]['buy'] = 0.00001
    acc.price_tables[ACC_CURRENCIES.EURUSD]['sell'] = 0.000009
    with pytest.raises(FundsExhausted):
        acc.positions[0].close()
    assert acc.funds == 0
    LOGGER.debug("PASSED test_funds_exhausted")



def test_close_positon():
    """test closing of a position"""
    LOGGER.debug("RUN test_close_position")
    # PARAM
    acc = Account("beginner", 1000)
    # make order
    acc.update_price(ACC_CURRENCIES.EURUSD)
    funds = acc.funds
    LOGGER.debug("RESULT funds - {}".format(funds))
    acc.make_order(MODE.BUY, ACC_CURRENCIES.EURUSD, 5000)
    # compare gain with funds
    LOGGER.debug("sleeping...")
    older_price = acc.price_tables[ACC_CURRENCIES.EURUSD]['buy']
    acc.price_tables[ACC_CURRENCIES.EURUSD]['buy'] = older_price + 0.1
    acc.positions[0].close()
    acc.price_tables[ACC_CURRENCIES.EURUSD]['buy'] = older_price
    LOGGER.debug("RESULT acc.funds - {}".format(acc.funds))
    assert acc.funds != funds
    LOGGER.debug("PASSED test_close_position")
