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
import numpy as np
import json
import yaml

from foreanalyzer.exceptions import CurrencyNotListed

LOGGER = logging.getLogger("foreanalyzer.internal")


# accepted currencies in analyzer
ACC_CURRENCIES = [
    "AUDUSD",
    "EURCHF",
    "EURGBP",
    "EURJPY",
    "EURUSD",
    "GBPUSD",
    "USDCAD",
    "USDCHF",
    "USDJPY"]


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
INVERTED_MODE = {'buy': 'sell', 'sell': 'buy'}


def read_ext_config():
    """read configuration file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.yml')
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    LOGGER.debug("read external yaml config")
    return config


def read_int_config():
    """read internal json config file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.json')
    with open(filename, 'r') as f:
        config = json.load(f)
        LOGGER.debug("read internal json config")
        return config


def write_int_config(data):
    """read internal json config file"""
    filename = os.path.join(OUTER_FOLDER_PATH, 'config.json')
    with open(filename, 'w') as f:
        config = json.dump(data, f)
        LOGGER.debug("write internal json config")


def resample_business(dataframe, timeframe_seconds):
    """Resample dataframe only with business day"""

    def DFresampler(input):
        if len(input) == 0:
            return None
        else:
            if input.name == "open":
                return input[0]
            elif input.name == "close":
                return input[-1]
            elif input.name == "high":
                return max(input)
            elif input.name == "low":
                return min(input)
            else:
                return input[-1]

    df = dataframe.resample(f"{timeframe_seconds}S").apply(DFresampler)
    return df[df.index.dayofweek < 5]


def resample_change_period(dataframe, new_period):
    def _get_val(series, ind):
        if len(series) > 0:
            return series[ind]
        else:
            return np.NAN

    df = dataframe.resample(f"{new_period}S").agg(
        {'open': lambda s: _get_val(s, 0), 'close': lambda s: _get_val(s,
         -1), 'high': lambda s: s.max(), 'low': lambda s: s.min()})
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
