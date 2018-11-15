"""
foreanalyzer.tables
~~~~~~~~~~~~~~~~~~~

Contains the table fot spread, min, margin, swap, ....
"""


# currency store model
class Currency(object):
    def __init__(self, spread, min_quantity, stnd_margin,
                 pro_margin, long_swap, short_swap):
        self.spread = spread
        self.min_quantity = min_quantity
        self.stnd_margin = stnd_margin
        self.pro_margin = pro_margin
        self.long_swap = long_swap
        self.short_swap = short_swap


# currency model stored on 181108
CURRENCIES = {
    "AUDUSD": Currency(0.00025, 2500, 0.0500, 0.0033, -0.000022, -0.000031),
    "EURCHF": Currency(0.00025, 2500, 0.0333, 0.0100, -0.000051, -0.000045),
    "EURGBP": Currency(0.00022, 2500, 0.0333, 0.0033, -0.000056, -0.000029),
    "EURJPY": Currency(0.02500, 2500, 0.0333, 0.0005, -0.007403, -0.001625),
    "EURUSD": Currency(0.00009, 2500, 0.0333, 0.0033, -0.000086,  0.000002),
    "GBPUSD": Currency(0.00015, 2500, 0.0333, 0.0033, -0.000087, -0.000027),
    "USDCAD": Currency(0.00035, 2500, 0.0333, 0.0033, -0.000029, -0.000038),
    "USDCHF": Currency(0.00023, 2500, 0.0333, 0.0050, -0.000001, -0.000072),
    "USDJPY": Currency(0.01500, 2500, 0.0333, 0.0033, -0.001578, -0.005208)
}
