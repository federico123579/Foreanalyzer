"""
tests.forex_python
~~~~~~~~~~~~~~~~~~

Test the forex_python module.
"""

from forex_python.converter import CurrencyRates
import pytest
from foreanalyzer._internal_utils import ACC_CURRENCIES


currencies = [(x.value[:3], x.value[3:]) for x in ACC_CURRENCIES]

@pytest.fixture(scope="function", params=currencies)
def get_rates(request):
    param = request.param
    cur = CurrencyRates()
    yield param
    rate = cur.get_rate(param[0], param[1])
    print(" test with conv_rate of {}".format(rate))

def test_rates(get_rates):
    param = get_rates
    print("RUN test_rates from {} to {}".format(param[0], param[1]))
