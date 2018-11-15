"""
tests.test_forex_python
~~~~~~~~~~~~~~~~~~

Test the forex_python module.
"""

from forex_python.converter import CurrencyRates
import pytest
from foreanalyzer._internal_utils import STR_CURRENCIES

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_forex_python")


currencies = [(x[:3], x[3:]) for x in STR_CURRENCIES]


@pytest.fixture(scope="function", params=currencies)
def get_rates(request):
    param = request.param
    cur = CurrencyRates()
    yield param
    rate = cur.get_rate(param[0], param[1])
    LOGGER.debug("PASSED test with conv_rate of {}".format(rate))


def test_rates(get_rates):
    param = get_rates
    LOGGER.debug("RUN test_rates from {} to {}".format(param[0], param[1]))
