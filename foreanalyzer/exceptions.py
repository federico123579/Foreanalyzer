# ~~~~ exceptions.py ~~~~
# forenalyzer.exceptions
# ~~~~~~~~~~~~~~~~~~~~~~~

import logging

from foreanalyzer.console import CliConsole


# ~ * LOGGER * ~
def ERROR(text):
    CliConsole().error(text, 'exception')


# ~ * EXCEPTIONS * ~
class InstrumentNotListed(Exception):
    def __init__(self, instrument):
        self.msg = f"Instrument {instrument} not listed"
        ERROR(self.msg)
        super().__init__(self.msg)


class LoginFailed(Exception):
    def __init__(self):
        self.msg = "Login failed"
        ERROR(self.msg)
        super().__init__(self.msg)


class NotConfigurated(Exception):
    def __init__(self):
        self.msg = "Missing configuration"
        ERROR(self.msg)
        super().__init__(self.msg)