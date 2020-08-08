
# ~~~~ utils.py ~~~~
# forenalyzer.utils
# ~~~~~~~~~~~~~~~~~~

import json
import logging
import os.path

import yaml

import foreanalyzer.globals as glob


# ~ * LOGGER * ~
LOGGER = logging.getLogger("foreanalyzer.utils")


# ~~~ * LOW LEVEL CONFIG FUNCTIONS * ~~~
def read_ext_config():
    """read configuration file"""
    filename = os.path.join(glob.OUTER_FOLDER_PATH, 'config.yml')
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    LOGGER.debug("read external yaml config")
    return config


def read_int_config():
    """read internal json config file"""
    filename = os.path.join(glob.OUTER_FOLDER_PATH, 'config.json')
    with open(filename, 'r') as f:
        config = json.load(f)
        LOGGER.debug("read internal json config")
        return config


def write_int_config(data):
    """read internal json config file"""
    filename = os.path.join(glob.OUTER_FOLDER_PATH, 'config.json')
    with open(filename, 'w') as f:
        json.dump(data, f)
        LOGGER.debug("write internal json config")


# ~~~ * SINGLETON * ~~~
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
