# ~~~~ api_handler.py ~~~~
# forenalyzer.api_handler
# ~~~~~~~~~~~~~~~~~~~~~~~~

from XTBApi.api import Client
import XTBApi.exceptions

from foreanalyzer.console import CliConsole
from foreanalyzer.exceptions import LoginFailed
import foreanalyzer.utils as utils


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "api"

def DEBUG(text, level=1):
    LOGGER().debug(text, PREFIX, level)


# ~~~ * HIGH LEVEL CLASSES * ~~~
class APIHandler(metaclass=utils.SingletonMeta):
    """handler of Api, use only for singleton"""

    def __init__(self):
        self.api = Client()
        self.status = 0

    def setup(self):
        """login with credentials in config"""
        if self.status:
            DEBUG("APIHandler already setup", 3)
            return
        config = utils.read_int_config()['credentials']
        try:
            response = self.api.login(config['username'], config['password'])
            DEBUG("logged in")
        except XTBApi.exceptions.CommandFailed:
            raise LoginFailed()
        self.status = 1
        DEBUG(f"{self.__class__.__name__} setup")
        return response

    def shutdown(self):
        """logout for symmetry"""
        if not self.status:
            DEBUG("APIHandler already shutdown", 3)
            return
        response = self.api.logout()
        self.status = 0
        DEBUG(f"{self.__class__.__name__} shutdown")
        return response
