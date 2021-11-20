# ~~~~ algo.py ~~~~
# forenalyzer.algo
# ~~~~~~~~~~~~~~~~~

import numpy as np
import pandas as pd
import talib.abstract as talabs

from foreanalyzer.console import CliConsole


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "indicators"

def DEBUG(text, level=2):
    LOGGER().debug(text, PREFIX, level)


# ~~~ * INDICATORS * ~~~
# checklist add new indicator
# [ ] add funtion below
# [ ] add to factory
# [ ] add to glob
def BBANDS(data, period=5, devup=2, devdw=2, matype=0):
    upperband, middleband, lowerband = talabs.BBANDS(
        data['close'], timeperiod=period, devup=devup, devdn=devdw, matype=matype)
    data[f'BBANDS_{period}_up'] = upperband
    data[f'BBANDS_{period}_md'] = middleband
    data[f'BBANDS_{period}_dw'] = lowerband
    DEBUG(f"set BolligerBands with {period} as period")        
    return data

def EMA(data, period=30):
    data[f'EMA_{period}'] = talabs.EMA(data['close'], timeperiod=period)
    DEBUG(f"set EMA with {period} as period")        
    return data

def SAR(data, acceleration=5.0, maximum=5.0):
    data['SAR'] = talabs.SAR(
        data['high'], data['low'], acceleration=acceleration, maximum=maximum)
    DEBUG(f"set SAR with {acceleration} as acceleration")        
    return data

def SMA(data, period=30):
    data[f'SMA_{period}'] = talabs.SMA(data['close'], timeperiod=period)
    DEBUG(f"set SMA with {period} as period")        
    return data


# ~~~ * MOMENTUM INDICATOR * ~~~
def RSI(data, period=14):
    data[f'RSI_{period}'] = talabs.RSI(data['close'], timeperiod=period)
    DEBUG(f"set RSI with {period} as period")
    return data


# ~~~ * OTHERS * ~~~
def SUPP_RES_LV(data, retest=2, tolerance=0.0004):
    """get support and resistance levels
    * retest: times of peaks on the same price necessary to define a level
    * tolerance: price difference tolerance for retest accceptance"""
    # ~ FIRST PHASE - uncovering peaks
    # ~ 0.239 milliseconds per loop MacBook13"intel_10th-20200901
    high_peaks = [] # define peaks list
    low_peaks = [] # define peaks list
    for i in range(len(data)):
        if i+2 >= len(data): # check if out of index
            continue # ignore and continue
        # check if we have a upper peak
        if (data['high'][i] > data['high'][i+1] and
                data['high'][i] > data['high'][i-1] and
                data['high'][i+1] > data['high'][i+2] and
                data['high'][i-1] > data['high'][i-2]):
            # append index and value of the peak
            high_peaks.append((i, data['high'][i]))
        # check if we have a lower peak
        if (data['low'][i] < data['low'][i+1] and
                data['low'][i] < data['low'][i-1] and
                data['low'][i+1] < data['low'][i+2] and
                data['low'][i-1] < data['low'][i-2]):
            # append index and value of the peak
            low_peaks.append((i, data['low'][i]))
    DEBUG(f"SR_LV: got {len(high_peaks)} higher peaks and {len(low_peaks)} lower peaks", 3)
    # ~ SECOND PHASE - getting levels depending on peaks close to each other
    # define series for later handling with rolling windows
    high_peaks = pd.Series(index=[i for i, _ in high_peaks], data=[x for _, x in high_peaks])
    low_peaks = pd.Series(index=[i for i, _ in low_peaks], data=[x for _, x in low_peaks])
    # func that merge or return 0 if condition not met
    def _merge_if_tolerance(window):
        if abs(window.iloc[0] - window.iloc[1]) < tolerance:
            return window.mean()
        else:
            return window.iloc[1]
    x = high_peaks.rolling(2).apply(_merge_if_tolerance) # merge high peaks
    support_levels = x[abs(x - x.shift(1)) > tolerance] # and select beyond tolerance
    x = low_peaks.rolling(2).apply(_merge_if_tolerance) # merge low peaks
    resistance_levels = x[abs(x - x.shift(1)) > tolerance] # and select beyond tolerance
    DEBUG(f"SR_LV: got {len(support_levels)} support levels and {len(resistance_levels)} resistance " +
          f"levels after retest", 3)
    # ~ THIRD PHASE
    data = data.reset_index()
    data[f'SUP_LV_{retest}'] = support_levels # set column
    data[f'SUP_LV_{retest}'].fillna(inplace=True, method='ffill') # fill with old levels
    shift_factor = 1
    while len(data[data['open'] > data[f'SUP_LV_{retest}']]) != 0:
        # define to replace because level is below open price
        to_replace = data[data['open'] > data[f'SUP_LV_{retest}']].index
        # define new index to reindex support levels
        new_index = [x for x in range(data.index[-1]+1)]
        # shift levels to shift_factor and the reindex and fill to_replace index
        reindexed_levels = support_levels.shift(shift_factor).reindex(new_index).fillna(method='ffill')
        # set values replaced in data
        data.loc[to_replace, f'SUP_LV_{retest}'] = reindexed_levels.loc[to_replace]
        shift_factor += 1 # pace and reiter
    data[f'RES_LV_{retest}'] = resistance_levels # set column
    data[f'RES_LV_{retest}'].fillna(inplace=True, method='ffill') # fill with old levels
    shift_factor = 1
    while len(data[data['open'] < data[f'RES_LV_{retest}']]) != 0:
        # define to replace because level is aboce open price
        to_replace = data[data['open'] < data[f'RES_LV_{retest}']].index
        # define new index to reindex resistance levels
        new_index = [x for x in range(data.index[-1]+1)]
        # shift levels to shift_factor and the reindex and fill to_replace index
        reindexed_levels = resistance_levels.shift(shift_factor).reindex(new_index).fillna(method='ffill')
        # set values replaced in data
        data.loc[to_replace, f'RES_LV_{retest}'] = reindexed_levels.loc[to_replace]
        shift_factor += 1 # pace and reiter
    data = data.set_index('datetime')
    DEBUG("support and resistance levels fixed to stay respectively above and below open price")
    return data
            

# ~~~ * FACTORY * ~~~
IndicatorFactory = {
    'BBANDS': BBANDS,
    'EMA': EMA,
    'SAR': SAR,
    'SMA': SMA,
    'RSI': RSI,
    'SR_LV': SUPP_RES_LV
}
