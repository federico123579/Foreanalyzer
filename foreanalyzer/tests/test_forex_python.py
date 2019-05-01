"""
tests.test_forex_python
~~~~~~~~~~~~~~~~~~

Test the forex_python module.
"""

import logging

import pytest
from forex_python.converter import CurrencyRates

from foreanalyzer._internal_utils import STR_CURRENCIES

LOGGER = logging.getLogger("foreanalyzer.tests.test_forex_python")


currencies = [(x[:3], x[3:]) for x in STR_CURRENCIES]


@pytest.fixture(scope="function", params=currencies)
def get_rates(request):
    param = request.param
    cur = CurrencyRates()
    yield param
    rate = cur.get_rate(param[0], param[1])
    LOGGER.debug("conversion rate of {}".format(rate))


def test_rates(get_rates):
    param = get_rates
    LOGGER.debug("test_rates from {} to {}".format(param[0], param[1]))
