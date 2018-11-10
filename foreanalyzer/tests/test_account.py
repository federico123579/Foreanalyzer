"""
test.test_account
~~~~~~~~~~~~~~~~~

Test account.
"""

import pytest
from foreanalyzer._internal_utils import ACC_CURRENCIES, MODE
from foreanalyzer.account import Account, Position
from foreanalyzer.tables import CURRENCIES


@pytest.fixture(scope="function", params=["beginner", "pro"])
def get_account(request):
    param = request.param
    print("RUN testing account {}".format(param))
    yield Account(param, 1000)
    print("PASSED test account {}".format(param))


orders_1 = [[MODE.BUY, x, 5000] for x in ACC_CURRENCIES]
orders_2 = [[MODE.BUY, x, 1] for x in ACC_CURRENCIES]
orders_1.extend(orders_2)

@pytest.fixture(scope="function", params=orders_1)
def get_orders(request):
    param = request.param
    print("RUN testing order {}".format(param[1]))
    yield param
    print("PASSED test order {}".format(param[1]))


def test_make_order(get_account, get_orders):
    """test the big function of make order"""
    # PARAMS
    acc = get_account
    param = get_orders
    # make order
    acc.update_price(param[1])
    print(acc.update_price(param[1]))
    print(acc.price_tables[param[1]])
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
    print("used_funds - {}".format(order.used_funds))
    assert acc.used_funds == order.used_funds
    # funds free updated
    assert acc.free_funds == acc.initial_funds - acc.used_funds
    # ...
    print("RUN test_make_order of {}".format(param[1]))
