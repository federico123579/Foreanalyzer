# ~~~~ cache_optimization.py ~~~~
# forenalyzer.cache_optimization
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import pickle
import shutil

from foreanalyzer.console import CliConsole


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "optimization"
# ~ * CONSTANTS * ~
CACHE_FOLDER = os.path.join(os.path.dirname(__file__), 'cache')
DEBUG_LEVEL = 3

def DEBUG(text):
    LOGGER().debug(text, PREFIX, DEBUG_LEVEL)

# ~~~ * HIGH LEVEL CACHE FUNCTIONS * ~~~
def clear_cache(filepath):
    """delete cache file"""
    if os.path.isfile(filepath):
        os.remove(filepath)
        DEBUG(f"{os.path.basename(filepath)} cache removed")
    else:
        DEBUG(f"{os.path.basename(filepath)} not existent to remove")


def load_cache(filepath):
    """load pickle cache"""
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    DEBUG(f"{os.path.basename(filepath)} cache loaded")
    return data


def save_cache(filepath, data):
    """save pickle cache"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    DEBUG(f"{os.path.basename(filepath)} cache saved")
        

def clear_all_cache():
    """empty cache folder - for test purposes"""
    for el in os.listdir(CACHE_FOLDER):
        DEBUG(f"CACHE CLEANING - removing {el}")
        shutil.rmtree(el)

# ~~~ * LOV LEVEL UTILITY FUNCTIONS * ~~~
def cache_path(folder_categories, file_prop):
    """get path of cache in cache folder"""
    path = os.path.join(CACHE_FOLDER, *folder_categories,
        '_'.join(file_prop) + '.pickle')
    return os.path.abspath(path)
