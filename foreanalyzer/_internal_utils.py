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
class CURRENCIES(Enum):
    AUDUSD = "AUDUSD"
    EURCHF = "EURCHF"
    EURGBP = "EURGBP"
    EURJPY = "EURJPY"
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDCAD = "USDCAD"
    USDCHF = "USDCHF"
    USDJPY = "USDJPY"


# accepted mode in analyzer
class MODE(Enum):
    BUY = 'buy'
    SELL = 'sell'


FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.dirname(os.path.dirname(__file__))
STR_CURRENCIES = [x.value for x in CURRENCIES]
INVERTED_MODE = {'buy': 'sell', 'sell': 'buy'}


def read_config():
    """read configuration file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.yml')
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    LOGGER.debug("read logger")
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
