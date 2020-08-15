# ~~~~ gloabls.py ~~~~
# forenalyzer.globals
# ~~~~~~~~~~~~~~~~~~~~

import os.path


# list of accepted instruments
ACCEPTED_INSTRUMENTS = ["EURUSD", "AUDUSD", "EURCHF",
                        "EURGBP", "EURJPY", "GBPUSD",
                        "USDCAD", "USDCHF", "USDJPY"]

# list of accepted plot handlers
ACCEPTED_PLOT = ['CDSPLT']

# list of accepted timeframes determinated by the API of the simulator
ACCEPTED_TIMEFRAMES = [300, 3600]

# folder pathes
FOLDER_PATH = os.path.dirname(__file__)
OUTER_FOLDER_PATH = os.path.dirname(os.path.dirname(__file__))

# supported Feeder in relation to plotter/grapher
SUPPORTED_FEEDERS = {
    'CDSPLT': ['XTBF01', 'ZIPF01']
}