# ~~~~ exceptions.py ~~~~
# forenalyzer.exceptions
# ~~~~~~~~~~~~~~~~~~~~~~~

import logging


# ~ * LOGGER * ~
LOGGER = logging.getLogger("foreanalyzer.exceptions")


# ~ * EXCEPTIONS * ~
class InstrumentNotListed(Exception):
    def __init__(self, instrument):
        self.msg = f"Instrument {instrument} not listed"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class NotConfigurated(Exception):
    def __init__(self):
        self.msg = "Missing configuration"
        LOGGER.error(self.msg)
        super().__init__(self.msg)