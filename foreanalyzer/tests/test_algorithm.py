"""
test.test_algorithm
~~~~~~~~~~~~~~~~~

Test algos.
"""

from io import StringIO

import numpy as np
import pandas as pd

from foreanalyzer.algorithm import SMA, AlgorithmExample001
from foreanalyzer.data_handler import normalize_df

# logger
import logging
LOGGER = logging.getLogger("foreanalyzer.tests.test_algorithm")
LOGGER.info("TESTING test_algorithm.py module")


csv_example = StringIO('''<TICKER>,<DTYYYYMMDD>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
                          EURUSD,20010102,230100,0.9507,0.9507,0.9507,0.9507,4
                          EURUSD,20010102,230200,0.9506,0.9506,0.9505,0.9505,4
                          EURUSD,20010102,230300,0.9505,0.9507,0.9505,0.9506,4
                          EURUSD,20010102,230400,0.9506,0.9506,0.9506,0.9506,4
                          EURUSD,20010102,230500,0.9506,0.9506,0.9506,0.9506,4
                          EURUSD,20010102,230600,0.9506,0.9506,0.9506,0.9506,4
                          EURUSD,20010102,230700,0.9505,0.9507,0.9505,0.9507,4
                          EURUSD,20010102,230800,0.9507,0.9507,0.9507,0.9507,4
                          EURUSD,20010102,230900,0.9507,0.9507,0.9507,0.9507,4
                          EURUSD,20010103,005000,0.9495,0.9496,0.9495,0.9496,4
                          EURUSD,20010103,005100,0.9496,0.9496,0.9496,0.9496,4
                          EURUSD,20010103,005200,0.9496,0.9496,0.9496,0.9496,4
                          EURUSD,20010103,005300,0.9495,0.9495,0.9495,0.9495,4
                          EURUSD,20010103,005400,0.9494,0.9494,0.9492,0.9492,4
                          EURUSD,20010103,005500,0.9492,0.9493,0.9492,0.9493,4
                          EURUSD,20010103,005600,0.9493,0.9497,0.9493,0.9497,4''')

def test_SMA():
    LOGGER.debug("RUN test_SMA")
    df = normalize_df(pd.read_csv(csv_example), 1000)
    # set period for testing
    period = 4
    sma = SMA(period)
    close_values = df['close'].values
    sma_values = sma.eval(df)['sma'].values
    calc_sma = []
    # add SMA
    for i, val in enumerate(close_values):
        i += 1  # scale up
        # calc other index margin
        i_p = i - period
        if i < period:  # append NaN
            calc_sma.append(np.nan)
        # if n (period) of values avaible
        elif i_p >= 0:
            # calc simple moving average sum(n1+n2+n3) / nn
            sma = sum(close_values[i_p:i]) / period
            # append sma
            calc_sma.append(sma)
    # check every value
    sma_values = pd.Series(sma_values).dropna()
    calc_sma = pd.Series(calc_sma).dropna()
    for i in range(len(sma_values)):
        assert sma_values.iloc[i] == calc_sma.iloc[i]
    LOGGER.debug(calc_sma.head())
    LOGGER.debug("PASSED test_SMA")


def test_feed():
    LOGGER.debug("RUN test_feed")
    algo = AlgorithmExample001()
    data = algo.feed()
    LOGGER.debug(data.tail())
    LOGGER.debug("PASSED test_feed")

