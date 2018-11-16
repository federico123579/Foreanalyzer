"""
foreanalyzer._internal_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

internal utils
"""

import json
import os
import os.path
import zipfile
from enum import Enum


# accepted currencies in analyzer
# WARNING: if you add a currency update also tables.py values
class ACC_CURRENCIES(Enum):
    AUDUSD = "AUDUSD"
    EURCHF = "EURCHF"
    EURGBP = "EURGBP"
    EURJPY = "EURJPY"
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDCAD = "USDCAD"
    USDCHF = "USDCHF"
    USDJPY = "USDJPY"


# mode buy or sell
class MODE(Enum):
    BUY = 'buy'
    SELL = 'sell'


FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.join(os.path.dirname(
    os.path.dirname(__file__)))
STR_CURRENCIES = [x.value for x in ACC_CURRENCIES]
INVERTED_MODE = {
    'buy': 'sell',
    'sell': 'buy'
}


# -[ SINGLETON ]-
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


def read_config():
    """read configuration file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.json')
    with open(filename, 'r') as f:
        config = json.load(f)
    return config


def unzip_data(folder, zip_file_basename):
    """unzip data from folder data outside of foreanalyzer"""
    # path
    filename = os.path.join(folder, zip_file_basename + '.zip')
    new_folder = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)
    # unzip
    if os.path.isfile(os.path.join(new_folder, zip_file_basename + '.txt')):
        return 0
    else:
        zip_file = zipfile.ZipFile(filename, 'r')
        zip_file.extractall(new_folder)
        zip_file.close()
        return 1
