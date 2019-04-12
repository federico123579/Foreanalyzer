"""
foreanalyzer._internal_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

internal utils
"""

import logging
import os
import os.path
import zipfile
from enum import Enum

import yaml

LOGGER = logging.getLogger("foreanalyzer.internal")


# accepted currencies in analyzer
class CURRENCY(Enum):
    AUDUSD = "AUDUSD"
    EURCHF = "EURCHF"
    EURGBP = "EURGBP"
    EURJPY = "EURJPY"
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDCAD = "USDCAD"
    USDCHF = "USDCHF"
    USDJPY = "USDJPY"


# accepted modes in analyzer
class MODE(Enum):
    buy = 0
    sell = 1


# status of components
class STATUS(Enum):
    OFF = 0
    ON = 1


# states of trades
class STATE(Enum):
    OPEN = 1
    CLOSED = 0


FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.dirname(os.path.dirname(__file__))
STR_CURRENCIES = [x.value for x in CURRENCY]
INVERTED_MODE = {'buy': 'sell', 'sell': 'buy'}


def read_config():
    """read configuration file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.yml')
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    LOGGER.debug("read config")
    return config


def unzip_data(folder, zip_file_basename: str):
    """unzip data from folder data outside of foreanalyzer"""
    # find path
    filename = os.path.join(folder, zip_file_basename + '.zip')
    new_folder = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)
    # unzip file
    if os.path.isfile(os.path.join(new_folder, zip_file_basename + '.csv')):
        return 0
    else:
        zip_file = zipfile.ZipFile(filename, 'r')
        zip_file.extractall(new_folder)
        zip_file.close()
        basename = os.path.join(new_folder, zip_file_basename)
        os.rename(basename + '.txt', basename + '.csv')
        return 1


class SingletonMeta(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    _instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super().__call__()
        return cls._instance
