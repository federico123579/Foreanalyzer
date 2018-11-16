"""
foreanalyzer.exceptions
~~~~~~~~~~~~~~~~~~~~~~~

All exceptions here.
"""

class OrderAborted(Exception):
    def __init__(self):
        self.msg = "Order aborted"
        super().__init__(self.msg)


class PriceNotUpdated(Exception):
    def __init__(self):
        self.msg = "Instrument non in price_tables"
        super().__init__(self.msg)


class FundsExhausted(Exception):
    def __init__(self):
        self.msg = "Funds exhausted"
        super().__init__(self.msg)
