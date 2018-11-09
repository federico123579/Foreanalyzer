"""
foreanalyzer._internal_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

internal utils
"""

from enum import Enum


# accepted currencies in analyzer
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


# mode buy or sell
class MODE(Enum):
    BUY = 'buy'
    SELL = 'sell'
