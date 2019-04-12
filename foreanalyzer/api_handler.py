"""
foreanalyzer.api_handler
~~~~~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

import logging

import XTBApi.exceptions
from XTBApi.api import Client

import foreanalyzer._internal_utils
from foreanalyzer.exceptions import LoginFailed

LOGGER = logging.getLogger("foreanalyzer.api_handler")


class ApiClient(metaclass=foreanalyzer._internal_utils.SingletonMeta):
    """handler of Api"""

    def __init__(self):
        self.api = Client()

    def setup(self):
        """login with credentials in config"""
        config = foreanalyzer._internal_utils.read_config()['account']
        try:
            response = self.api.login(config['username'], config['password'])
        except XTBApi.exceptions.CommandFailed:
            raise LoginFailed()
        LOGGER.debug(f"{self.__class__.__name__} setup")
        return response

    def shutdown(self):
        """logout for symmetry"""
        response = self.api.logout()
        LOGGER.debug(f"{self.__class__.__name__} shutdown")
        return response
