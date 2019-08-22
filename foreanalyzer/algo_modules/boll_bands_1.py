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

    def _close_long_signal_formula(self, datetime_range, signals_df, df_obj):
        catch = datetime_range[
            datetime_range['close'] > datetime_range['BollBands_20_ma']]
        long_signal = catch.iloc[0] if not catch.empty else datetime_range[-1]
        return long_signal

    def _close_short_signal_formula(self, datetime_range, signals_df, df_obj):
        catch = datetime_range[
            datetime_range['close'] < datetime_range['BollBands_20_ma']]
        short_signal = catch.iloc[0] if not catch.empty else datetime_range[-1]
        return short_signal
