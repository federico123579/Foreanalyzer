"""
foreanalyzer.algo_modules.boll_bands_1.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on Bolliger Bands with timeframe of an hour.
"""

import logging

from foreanalyzer._internal_utils import read_config
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
        _sma = self._add_indicator_conf('SMA', period=20)
        _boll = self._add_indicator_conf('BOLL', period=20)
        _indi_conf = [_sma, _boll]
        super().__init__(_name, _indi_conf)

    def _open_long_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        long_raw_signals = df[df['close'] < df['BollBands_20_down']]
        return long_raw_signals

    def _open_short_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        short_raw_signals = df[df['close'] > df['BollBands_20_up']]
        return short_raw_signals
