# ~~~~ algo.py ~~~~
# forenalyzer.algo
# ~~~~~~~~~~~~~~~~~

import talib.abstract as talabs

from foreanalyzer.console import CliConsole


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "indicators"

def DEBUG(text, level=3):
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


# ~~~ * FACTORY * ~~~
IndicatorFactory = {
    'BBANDS': BBANDS,
    'EMA': EMA,
    'SAR': SAR,
    'SMA': SMA,
    'RSI': RSI
}
