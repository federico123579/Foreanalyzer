"""
foreanalyzer.exceptions
~~~~~~~~~~~~~~~~~~~~~~~

All exceptions here.
"""

import logging

LOGGER = logging.getLogger("foreanalyzer.exceptions")


class FundsExhausted(Exception):
    def __init__(self):
        self.msg = "Funds exhausted"
        LOGGER.warning(self.msg)
        super().__init__(self.msg)


class LoginFailed(Exception):
    def __init__(self):
        self.msg = "Login failed"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class NotLogged(Exception):
    def __init__(self):
        self.msg = "Login needed not done yet"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class IndicatorNotExecuted(Exception):
    def __init__(self):
        self.msg = "Indicator not executed yet"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class IndicatorLenError(Exception):
    def __init__(self, val, dat):
        self.msg = f"Len of values {val} is different from dataframe len {dat}"
        LOGGER.error(self.msg)
        super().__init__(self.msg)

# class OrderAborted(Exception):
#     def __init__(self):
#         self.msg = "Order aborted"
#         super().__init__(self.msg)
#
#
# class PriceNotUpdated(Exception):
#     def __init__(self):
#         self.msg = "Instrument non in price_tables"
#         super().__init__(self.msg)
#
#
# class FundsExhausted(Exception):
#     def __init__(self):
#         self.msg = "Funds exhausted"
#         super().__init__(self.msg)
#
#
# class PeriodNotExpected(Exception):
#     def __init__(self):
#         self.msg = "Period not expected in algorithm created span"
#         super().__init__(self.msg)
