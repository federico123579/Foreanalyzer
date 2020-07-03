"""
foreanalyzer.exceptions
~~~~~~~~~~~~~~~~~~~~~~~

All exceptions here.
"""

import logging

LOGGER = logging.getLogger("foreanalyzer.exceptions")


class AlgorithmNotExecuted(Exception):
    def __init__(self):
        self.msg = "Algorithm not executed yet"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class CurrencyNotListed(Exception):
    def __init__(self, currency):
        self.msg = f"Currency {currency} not listed"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class FundsExhausted(Exception):
    def __init__(self):
        self.msg = "Funds exhausted"
        LOGGER.warning(self.msg)
        super().__init__(self.msg)


class IndicatorError(Exception):
    def __init__(self):
        self.msg = "Indicator error (may be the filter)"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class IndicatorLenError(Exception):
    def __init__(self, val, dat):
        self.msg = f"Len of values {val} is different from dataframe len {dat}"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class IndicatorNotExecuted(Exception):
    def __init__(self):
        self.msg = "Indicator not executed yet"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class IndicatorNotListed(Exception):
    def __init__(self, indicator):
        self.msg = f"Indicator {indicator} not listed"
        LOGGER.error(self.msg)
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


class NotConfigurated(Exception):
    def __init__(self):
        self.msg = "Missing configuration"
        LOGGER.error(self.msg)
        super().__init__(self.msg)