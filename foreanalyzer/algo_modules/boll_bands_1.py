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
        _sma1 = self._add_indicator_conf('SMA', period=12)
        _sma2 = self._add_indicator_conf('SMA', period=50)
        _indi_conf = [_sma1, _sma2]
        super().__init__(_name, _indi_conf)
        # defining stop loss and take profit
        self.stop_loss = _conf[_name]['stop_loss']
        self.take_profit = _conf[_name]['take_profit']

    def _open_long_signal_formula(self, df_obj):
        df = df_obj.resample(self.update_freq).dropna()
        import pickle
        with open("test_signals.pickle", 'wb') as f:
            pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
        long_raw_signals = df[(df['sma_12'] < df['sma_50']) &
                             (df['high'] < df['sma_12'])]
        return long_raw_signals

    def _open_short_signal_formula(self, df_obj):
        df = df_obj.resample(self.update_freq).dropna()
        short_raw_signals = df[(df['sma_12'] > df['sma_50']) &
                              (df['low'] > df['sma_12'])]
        return short_raw_signals

    def _close_long_signal_formula(self, df_r, open_signal, df_obj):
        # calculate entry
        catch = df_r[(df_r['close'] >= df_r['sma_50'])]
        catch = catch.iloc[[0]] if not catch.empty else df_r.iloc[[-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_long(df_r, open_signal)
        tp_catch = self._get_take_profit_on_long(df_r, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]

    def _close_short_signal_formula(self, df_r, open_signal, df_obj):
        # calculate entry
        catch = df_r[(df_r['close'] <= df_r['sma_50'])]
        catch = catch.iloc[[0]] if not catch.empty else df_r.iloc[[-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_short(df_r, open_signal)
        tp_catch = self._get_take_profit_on_short(df_r, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]


class BolligerBands2(BaseAlgorithm):
    """Based on Bolliger Bands with timeframe of an hour"""

    def __init__(self):
        _name = self.__class__.__name__
        _conf = read_config()
        # defining timeframe
        self.timeframe = _conf[_name]['timeframe']
        # add indicators
        _boll = self._add_indicator_conf('BOLL', period=30, multiplier=2.5)
        _indi_conf = [_boll]
        super().__init__(_name, _indi_conf)
        # defining stop loss and take profit
        self.stop_loss = _conf[_name]['stop_loss']
        self.take_profit = _conf[_name]['take_profit']

    def _open_long_signal_formula(self, df_obj):
        df = df_obj.resample(self.update_freq).dropna()
        long_raw_signals = df[df['close'] < df['BollBands_30_down']]
        return long_raw_signals

    def _open_short_signal_formula(self, df_obj):
        df = df_obj.resample(self.update_freq).dropna()
        short_raw_signals = df[df['close'] > df['BollBands_30_up']]
        return short_raw_signals

    def _close_long_signal_formula(self, df_r, open_signal, df_obj):
        # calculate entry
        catch = df_r[(df_r['close'] > df_r['BollBands_30_ma']) |
                     (df_r['BollBands_30_width'] >= 1.7)]
        catch = catch.iloc[[0]] if not catch.empty else df_r.iloc[
            [-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_long(df_r, open_signal)
        tp_catch = self._get_take_profit_on_long(df_r, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]

    def _close_short_signal_formula(self, df_r, open_signal, df_obj):
        # calculate entry
        catch = df_r[(df_r['close'] < df_r['BollBands_30_ma']) |
                     (df_r['BollBands_30_width'] >= 1.7)]
        catch = catch.iloc[[0]] if not catch.empty else df_r.iloc[
            [-1]]
        # stop loss and take profit
        sl_catch = self._get_stop_loss_on_short(df_r, open_signal)
        tp_catch = self._get_take_profit_on_short(df_r, open_signal)
        _df = pd.concat([catch, sl_catch, tp_catch]).sort_index()
        return _df.iloc[0]
