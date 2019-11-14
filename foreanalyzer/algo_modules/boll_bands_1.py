"""
foreanalyzer.algo_modules.boll_bands_1.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on Bolliger Bands with timeframe of an hour.
"""

import logging

import pandas as pd

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
        # defining stop loss and take profit
        self.stop_loss = _conf[_name]['stop_loss']
        self.take_profit = _conf[_name]['take_profit']

    def _open_long_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        long_raw_signals = df[df['close'] < df['BollBands_20_down']]
        return long_raw_signals

    def _open_short_signal_formula(self, df_obj):
        df = df_obj.resample(self.timeframe).dropna()
        short_raw_signals = df[df['close'] > df['BollBands_20_up']]
        return short_raw_signals

    def _close_long_signal_formula(self, datetime_range, open_signal, df_obj):
        # calculate entry
        catch = datetime_range[
            (datetime_range['close'] > datetime_range['BollBands_20_ma']) |
            (datetime_range['BollBands_20_width'] > 2)]
        catch = catch.iloc[[0]] if not catch.empty else datetime_range.iloc[
            [-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_long(datetime_range, open_signal)
        tp_catch = self._get_take_profit_on_long(datetime_range, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]

    def _close_short_signal_formula(self, datetime_range, open_signal, df_obj):
        # calculate entry
        catch = datetime_range[
            (datetime_range['close'] < datetime_range['BollBands_20_ma']) |
            (datetime_range['BollBands_20_width'] > 2)]
        catch = catch.iloc[[0]] if not catch.empty else datetime_range.iloc[
            [-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_short(datetime_range, open_signal)
        tp_catch = self._get_take_profit_on_short(datetime_range, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]
