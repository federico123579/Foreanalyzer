"""
foreanalyzer.api_handler
~~~~~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

import logging

import XTBApi.exceptions
from XTBApi.api import Client

import foreanalyzer._internal_utils as internal
from foreanalyzer.exceptions import LoginFailed

LOGGER = logging.getLogger("foreanalyzer.api_handler")


class ApiClient(metaclass=internal.SingletonMeta):
    """handler of Api, use only for singleton"""

    def __init__(self):
        self.api = Client()
        self.status = internal.STATUS.OFF

    def setup(self):
        """login with credentials in config"""
        if self.status == internal.STATUS.ON:
            LOGGER.debug("ApiClient already setup")
            return
        config = internal.read_int_config()['account']
        try:
            response = self.api.login(config['username'], config['password'])
        except XTBApi.exceptions.CommandFailed:
            raise LoginFailed()
        self.status = internal.STATUS.ON
        LOGGER.debug(f"{self.__class__.__name__} setup")
        return response

    def shutdown(self):
        """logout for symmetry"""
        if self.status == internal.STATUS.OFF:
            LOGGER.debug("ApiClient already shutdown")
            return
        response = self.api.logout()
        self.status = internal.STATUS.OFF
        LOGGER.debug(f"{self.__class__.__name__} shutdown")
        return response
