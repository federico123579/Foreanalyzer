"""
foreanalyzer.algo_modules.boll_bands_1.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on Bolliger Bands with timeframe of an hour.
"""

import logging

import pandas as pd

from foreanalyzer._internal_utils import MODE, read_config
from foreanalyzer.algorithm import BaseAlgorithm


LOGGER = logging.getLogger("foreanalyzer.mod.boll_bands_1")


# ===================== BOLLIGER BANDS 1 =======================

class BolligerBands1(BaseAlgorithm):
    """Based on Bolliger Bands with timeframe of an hour"""

    def __init__(self):
        _name = self.__class__.__name__
        _conf = read_config()
        # defining timeframe
        self.timeframe = _conf[_name]['timeframe']
        # add indicators
        _boll = self._add_indicator_conf('BOLL', period=20)
        _indi_conf = [_boll]
        super().__init__(_name, _indi_conf)

    def _open_long_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        long_raw_signals = df[df['close'] < df['BollBands_20_down']]
        return long_raw_signals

    def _open_short_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        short_raw_signals = df[df['close'] > df['BollBands_20_up']]
        return short_raw_signals

    def _close_signal_formula(self, df_obj, signals_df):
        df = df_obj.resample(self.update_freq).dropna()
        signals = []
        for datetime, mode in signals_df.iteritems():
            datetime_range = df.loc[datetime:]
            if mode == MODE.buy.value:
                catch = datetime_range[
                    datetime_range['close'] > datetime_range['BollBands_20_ma']]
            elif mode == MODE.sell.value:
                catch = datetime_range[
                    datetime_range['close'] < datetime_range['BollBands_20_ma']]
            signal = catch.iloc[0] if not catch.empty else datetime_range[-1]
            open_pr = datetime_range.iloc[0]['open']
            close_pr = signal['close']
            signals.append([datetime, signal.name, open_pr, close_pr, mode])
        return pd.DataFrame(columns=['open_datetime', 'close_datetime',
                                     'open_price', 'close_price', 'mode'],
                            data=signals)
