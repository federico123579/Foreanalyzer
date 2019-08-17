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

from foreanalyzer.exceptions import CurrencyNotListed

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
    EXECUTED = 2


# states of trades
class STATE(Enum):
    OPEN = 1
    CLOSED = 0
    EVALUATED = 2


FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.dirname(os.path.dirname(__file__))
STR_CURRENCIES = [x.value for x in CURRENCY]
INVERTED_MODE = {'buy': 'sell', 'sell': 'buy'}


def conv_str_enum(string_to_conv, enu_to_conv):
    if not isinstance(string_to_conv, enu_to_conv):
        if string_to_conv in [x.value for x in enu_to_conv]:
            return [curr for curr in CURRENCY
                    if curr.value == string_to_conv][0]
        else:
            raise CurrencyNotListed(string_to_conv)
    else:
        return string_to_conv


def read_config():
    """read configuration file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.yml')
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    LOGGER.debug("read config")
    return config


def resample_business(dataframe, timeframe_seconds):
    """Resample dataframe only with business day"""
    df = dataframe.resample(f"{timeframe_seconds}S").asfreq()
    return df[df.index.dayofweek < 5]



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


class StatusComponent(object):
    """class for components with status"""

    def __init__(self):
        self.status = STATUS.OFF

    def setup(self):
        self.status = STATUS.ON
        LOGGER.debug(f"{self.__class__.__name__} setup")

    def shutdown(self):
        self.status = STATUS.OFF
        LOGGER.debug(f"{self.__class__.__name__} shutdown")


class LoggingContext(object):
    def __init__(self, logger, level=None, handler=None, close=True):
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close

    def __enter__(self):
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        # implicit return of None => don't swallow exceptions
