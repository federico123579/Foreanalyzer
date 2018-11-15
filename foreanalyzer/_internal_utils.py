"""
foreanalyzer._internal_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

internal utils
"""

import json
import os.path
from enum import Enum


# accepted currencies in analyzer
# WARNING: if you add a currency update also tables.py values
class ACC_CURRENCIES(Enum):
    AUDUSD = "AUDUSD"
    EURCHF = "EURCHF"
    EURGBP = "EURGBP"
    EURRUB = "EURRUB"
    EURJPY = "EURJPY"
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDCAD = "USDCAD"
    USDCHF = "USDCHF"
    USDRUB = "USDRUB"
    USDJPY = "USDJPY"


STR_CURRENCIES = [x.value for x in ACC_CURRENCIES]


# mode buy or sell
class MODE(Enum):
    BUY = 'buy'
    SELL = 'sell'


INVERTED_MODE = {
    'buy': 'sell',
    'sell': 'buy'
}


# -[ SINGLETON ]-
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


def read_config():
    """read configuration file"""
    filename = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'config.json')
    with open(filename, 'r') as f:
        config = json.load(f)
    return config
