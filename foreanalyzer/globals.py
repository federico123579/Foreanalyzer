# ~~~~ gloabls.py ~~~~
# forenalyzer.globals
# ~~~~~~~~~~~~~~~~~~~~

import os.path


# list of accepted instruments
ACCEPTED_INSTRUMENTS = ["EURUSD"]

# list of accepted timeframes determinated by the API of the simulator
ACCEPTED_TIMEFRAMES = []

# folder pathes
FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.dirname(os.path.dirname(__file__))