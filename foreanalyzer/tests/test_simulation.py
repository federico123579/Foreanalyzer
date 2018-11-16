"""
tests.test_simulation
~~~~~~~~~~~~~~~~~~

Test the simulation module.
"""

import pytest
from foreanalyzer.simulation import AccountSimulated
from foreanalyzer._internal_utils import ACC_CURRENCIES, MODE

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_simulation")
LOGGER.info("TESTING test_simulation.py module")


@pytest.fixture(scope="module")
def get_account():
    return AccountSimulated()


def test_config(get_account):
    """test the config init dict"""
    LOGGER.debug("RUN test_config")
    acc = get_account
    assert 'simulation' in acc.config
    LOGGER.debug("PASSED test_config")


def test_simulate(get_account):
    """test the simulate method"""
    LOGGER.debug("RUN test_simulate")
    acc = get_account
    old_funds = acc.funds
    EURUSD = ACC_CURRENCIES.EURUSD
    # make order
    acc.update_price(EURUSD)
    acc.make_order(MODE.BUY, EURUSD, 5000)
    # simulate change of price
    acc.simulate(EURUSD, 1.13400, 1.12300)
    price_table = {'buy': 1.13400, 'sell': 1.12300}
    assert acc.price_tables[EURUSD] == price_table
    # close position
    pos = acc.positions[0]
    LOGGER.debug("RESULT gain of pos - {}".format(pos.gain))
    pos.close()
    assert acc.funds != old_funds
    LOGGER.debug("PASSED test_simulate")
