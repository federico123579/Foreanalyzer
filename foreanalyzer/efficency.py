"""
foreanalyzer.efficency
~~~~~~~~~~~~~~~~~~~~~~

Module aimed to improve efficency of algo analis.
"""

import logging
import os.path

from foreanalyzer._internal_utils import CURRENCY
from foreanalyzer.data_handler import DataHandler

LOGGER = logging.getLogger("foreanalyzer.efficency")


def init_normalised_dataframes(range_of_values, currencies=None):
    """load and normalise for all currencies all range of values needed
    and save them as pickle files"""
    _count = 0  # count for logging reasons
    if not currencies:  # check if acceptable
        currencies = [curr for curr in CURRENCY]
    else:
        currencies = [CURRENCY(curr) for curr in currencies]
    # convert to a list if is only one value
    if isinstance(range_of_values, int):
        range_of_values = [range_of_values]
    # iterate and save
    for curr_range in range_of_values:
        dh = DataHandler(curr_range)
        for curr in currencies:
            df = dh.dataframes[curr]
            # if already exists move on
            if os.path.isfile(df.get_pickle_path()):
                continue
            df.load()  # save pickle
            df.unload()  # free RAM
            _count += 1
    LOGGER.debug(f"{_count} normalised dataframes saved on pickle files")
