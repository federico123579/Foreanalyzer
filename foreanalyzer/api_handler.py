"""
foreanalyzer.api_handler
~~~~~~~~~~~~~~~~~~~~~~~~

Store the simulated Account object.
"""

from XTBApi.api import Client

import foreanalyzer._internal_utils


class ApiClient(metaclass=foreanalyzer._internal_utils.SingletonMeta):
    """handler of Api"""

    def __init__(self):
        self.api = Client()

    def login(self):
        """login with credentials in config"""
        config = foreanalyzer._internal_utils.read_config()['account']
        return self.api.login(config['username'], config['password'])

    def logout(self):
        """logout for symmetry"""
        return self.api.logout()
