"""
foreanalyzer.algorithm
~~~~~~~~~~~~~~~~~~~~~~~

Base algorithm module.
"""

import abc
import logging
import os.path
import pickle

import pandas as pd

import foreanalyzer._internal_utils as internal
import foreanalyzer.algo_components as alco
import foreanalyzer.exceptions as exc
from foreanalyzer.data_handler import DataHandler, LatestDataHandler

LOGGER = logging.getLogger("foreanalyzer.algo")


# ============================== ALGORITHM ==============================
# BaseAlgorithm configured from config.yml
# This object when called for setup init a list of indicators with their
# respective parameters and after having set up a personalized instace
# of each of them in a respective dataframe object call them and submit.
# Doing this every indicator is inited and executed on setup and given
# access from dataframe object.
# ============================== ALGORITHM ==============================

class BaseAlgorithm(metaclass=abc.ABCMeta):
    """Base Algorithm implementation
    Read conf from imput and accept indicators and args for them"""

    def __init__(self, name: str, indicators: list):
        """
        indicator must be a list like this:
            indicators = [{'name': "SMA", 'args':
                             {'period': .., 'timeframe': ..}}]
        """
        config = internal.read_config()
        if name not in config.keys():
            raise ValueError(f"{name} not in config")
        for indi in indicators:
            if indi['name'] not in alco.IndicatorFactory.keys():
                raise exc.IndicatorNotListed(indi['name'])
        self.config = config[name]
        self.name = name
        self.timeframe: int
        self.take_profit = None
        self.stop_loss = None
        self.save_for_eff = self.config['save_for_eff']
        self.load_for_eff = self.config['load_for_eff']
        self.update_freq = self.config['update_freq']
        self.start_analysis = self.config['start_analysis']
        self.duplicate_protection = self.config['duplicate_protection']
        currencies = self.config['currencies']
        self.currencies = [internal.conv_str_enum(curr, internal.CURRENCY)
                           for curr in currencies]
        range_of_values = self.config['range_of_values']
        #self._data_handler = DataHandler(range_of_values)
        self._data_handler = LatestDataHandler(self.update_freq, self.start_analysis)
        self._indicators = indicators  # list of indicator configuration
        self._stock_data = self._data_handler.dataframes
        self.dataframes = {}  # store dataframe objects
        self.status = {'exe': 0}
        LOGGER.debug("BaseAlgorithm inited")

    @abc.abstractmethod
    def _close_long_signal_formula(self, datetime_range, open_signal, df_obj):
        """Accept as input the range of values after the open signal, df_obj
        and the dataframe output of self.get_open_signals and return a
        dataframe with open_date and close_date"""

    @abc.abstractmethod
    def _close_short_signal_formula(self, datetime_range, open_signal, df_obj):
        """Accept as input the range of values after the open signal, df_obj
        and the dataframe output of self.get_open_signals and return a
        dataframe with open_date and close_date"""

    @abc.abstractmethod
    def _open_short_signal_formula(self, df_obj):
        """Return a list of sell signals, dateteimes with index
        return a dataframe objects"""

    def _add_indicator_conf(self, name_of_indicator, **kwargs):
        """create a configuration of an indicator"""
        if name_of_indicator not in alco.IndicatorFactory.keys():
            raise exc.IndicatorNotListed(name_of_indicator)
        # add timeframe from algo
        kwargs.update({'timeframe': self.timeframe})
        indicator_conf = {
            'name': name_of_indicator,
            'args': kwargs}
        return indicator_conf

    def _check_if_setup(self):
        """check if algo has already been executed"""
        if not self.status['exe']:
            raise exc.AlgorithmNotExecuted()

    def _get_stop_loss_on_long(self, dtime_range, close_sig):
        """get stop loss"""
        if self.stop_loss is not None:
            _df = dtime_range[
                dtime_range['close'] <= close_sig['close'] - self.stop_loss]
            return _df.iloc[[0]] if not _df.empty else dtime_range.iloc[[-1]]
        return dtime_range.iloc[[-1]]

    def _get_stop_loss_on_short(self, dtime_range, close_sig):
        """get stop loss"""
        if self.stop_loss is not None:
            _df = dtime_range[
                dtime_range['close'] >= close_sig['close'] + self.stop_loss]
            return _df.iloc[[0]] if not _df.empty else dtime_range.iloc[[-1]]
        return dtime_range.iloc[[-1]]

    def _get_take_profit_on_long(self, dtime_range, close_sig):
        """get take profit"""
        if self.take_profit is not None:
            _df = dtime_range[
                dtime_range['close'] >= close_sig['close'] + self.take_profit]
            return _df.iloc[[0]] if not _df.empty else dtime_range.iloc[[-1]]
        return dtime_range.iloc[[-1]]

    def _get_take_profit_on_short(self, dtime_range, close_sig):
        """get take profit"""
        if self.take_profit is not None:
            _df = dtime_range[
                dtime_range['close'] <= close_sig['close'] - self.take_profit]
            return _df.iloc[[0]] if not _df.empty else dtime_range.iloc[[-1]]
        return dtime_range.iloc[[-1]]

    def _open_long_signal_formula(self, df_obj):
        """Return a list of buy signals, dateteimes with index
        return a dataframe objects"""

    def _init_indicators(self):
        """Init indicators here
        Indicators are inited here and set as attr in dataframe objects
        for each of currencies listened."""
        for currency in self.currencies:
            for indicator in self._indicators:
                dataframe_obj = self.dataframes[currency]
                factory_name = indicator['name']
                LOGGER.debug(f"setting {factory_name} for {currency.value}")
                _indicator = alco.IndicatorFactory[factory_name](
                    dataframe_obj.dataframe, **indicator['args'])
                setattr(dataframe_obj, _indicator.column_name, _indicator)
                dataframe_obj.add_indicator(_indicator.column_name)

    def _execute_indicators(self):
        """Execute all indicators
        Execute all indicators listened in self._indicators, given by
        init and submit their values in dataframe object."""
        for currency in self.currencies:
            df = self.dataframes[currency]
            for indicator in df.indicator_names:
                LOGGER.debug(f"executing {indicator} for {currency}")
                getattr(df, indicator).submit()

    def _remove_duplicates(self, raw_signals, level=8):
        """Removes signals too close to each other, taking a single one
        from a more signals, level represent the number of timeframe interval
        to wait before a new signal can be verified"""

        def _tot_secs(dt_df):
            return dt_df.diff().map(lambda x: x.total_seconds())

        LOGGER.debug("removing duplicates...")
        interval = self.timeframe * level
        datetimes = pd.Series(raw_signals)
        while len(datetimes[_tot_secs(datetimes) < interval]) > 0:
            index_to_drop = datetimes[_tot_secs(datetimes) <= interval].index
            pair_count = 2 # used to drop alternate
            for ind in index_to_drop:
                if pair_count % 2 == 0:
                    datetimes.drop(index=ind, inplace=True)
                pair_count += 1
        reduced_signals = datetimes[_tot_secs(datetimes) > interval]
        LOGGER.debug(f"Signals reduced to {len(reduced_signals)}")
        return reduced_signals

    def _get_pickle_path_eff(self):
        """save a pickle for later uses, improve efficiency over various
        iterations"""
        ind = '_'.join([f"{x['name']}_{x['args']['period']}" for x in
                        self._indicators])
        file_name = f"{self.name}_{self.timeframe}_{ind}.pickle"
        return os.path.join(internal.FOLDER_PATH, 'algo_efficency', file_name)

    def _load_pickle_eff(self):
        """save a pickle for later uses, improve efficiency over various
        iterations"""
        file_path = self._get_pickle_path_eff()
        if os.path.isfile(file_path) and self.load_for_eff:
            LOGGER.debug("LOADING algo from pickle")
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        else:
            return self

    def _save_pickle_eff(self):
        """save a pickle for later uses, improve efficiency over various
        iterations"""
        file_path = self._get_pickle_path_eff()
        if not os.path.isfile(file_path) or self.save_for_eff:
            LOGGER.debug("saving algo pickle")
            with open(file_path, 'wb') as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def setup(self):
        """Setup for the algo, init and execute indicators
        Call the setup directives, initing and executing all indicators."""
        if self.status['exe'] == 1:
            LOGGER.debug("BaseAlgo already set up")
            return
        for currency in self.currencies:
            self.dataframes[currency] = alco.AlgoDataframe(
                currency, self._stock_data[currency].load())
        self._init_indicators()
        self._execute_indicators()
        self.status['exe'] = 1
        self._save_pickle_eff()
        LOGGER.debug("BaseAlgorithm setup")

    def get_close_signals(self, currency, signals_df):
        """get the output of self.get_open_signals and return close signals"""
        df_obj = self.dataframes[currency]
        df = df_obj.resample(self.update_freq).dropna()
        signals = []
        for datetime, mode in signals_df.iteritems():
            if datetime not in df.index:
                LOGGER.debug(f"{datetime} bypassed")
                continue
            datetime_range = df.loc[datetime:]
            if mode == internal.MODE.buy.value:
                signal = self._close_long_signal_formula(
                    datetime_range, df.loc[datetime], df_obj)
            elif mode == internal.MODE.sell.value:
                signal = self._close_short_signal_formula(
                    datetime_range, df.loc[datetime], df_obj)
            open_pr = df.loc[datetime]['open']
            close_pr = signal['close']
            # TODO: remove width
            signals.append([datetime, signal.name, open_pr, close_pr, mode])
        LOGGER.debug(f"got close signals")
        # TODO: remove width
        return pd.DataFrame(columns=['open_datetime', 'close_datetime',
                                     'open_price', 'close_price', 'mode'],
                            data=signals)

    def get_open_signals(self, currency):
        """get the open signals for a currency, polished and ready to be
        executed on the market"""
        df_obj = self.dataframes[currency]
        df_obj.merge_indicators()
        long_signals = self._open_long_signal_formula(df_obj).index
        short_signals = self._open_short_signal_formula(df_obj).index
        LOGGER.debug(f"got {len(long_signals) + len(short_signals)} raw signals")
        reduced_long_signals = self._remove_duplicates(
            long_signals, level=self.duplicate_protection)
        reduced_short_signals = self._remove_duplicates(
            short_signals, level=self.duplicate_protection)
        long_signals = pd.Series(index=reduced_long_signals,
                                 data=internal.MODE.buy.value)
        short_signals = pd.Series(index=reduced_short_signals,
                                  data=internal.MODE.sell.value)
        signals = pd.concat([long_signals, short_signals]).sort_index()
        LOGGER.debug(f"got a total of {len(signals)} true signals")
        return signals
