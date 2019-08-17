"""
tests.test_simulation
~~~~~~~~~~~~~~~~~~

Test the simulation module.
"""

import logging
import os.path
import pickle

import pandas as pd

from foreanalyzer._internal_utils import CURRENCY, MODE, OUTER_FOLDER_PATH
from foreanalyzer.account import Account
from foreanalyzer.algo_components import SMA
from foreanalyzer.algorithm import BaseAlgorithm

LOGGER = logging.getLogger("foreanalyzer.tests.test_simulation")


def test_SMA_Simulation():
    # set up conf for the algorithm
    indicators = [
        {'name': 'SMA',
        'args': {'period': 10, 'timeframe': 86400}},
        {'name': 'EMA',
        'args': {'period': 20, 'timeframe': 86400}}]
    algo = BaseAlgorithm('TestAlgo', indicators)
    account = Account(1000)
    LOGGER.debug("components inited")
    algo.setup()
    account.setup()
    LOGGER.debug("components setup")
    df_obj = algo.dataframes[CURRENCY.EURUSD]
    _indicator_names_str = ", ".join([x for x in df_obj.indicator_names])
    LOGGER.debug(f"got df_obj and indicators {_indicator_names_str}")
    df_obj.merge_indicators()
    res_df = df_obj.resample(3600).dropna()
    LOGGER.debug(f"resampled & merged dataframe to {len(res_df)}")
    # DEFINE OPEN ENTRIES
    res_df.insert(0, 'count', range(len(res_df)))
    _entries_1 = res_df[res_df['ema_20'] < res_df['sma_10']]
    _open_entries_full = _entries_1[_entries_1['count'].diff() != 1]
    _open_entries = _open_entries_full.index
    LOGGER.debug(f"got {len(_open_entries)} open entries")
    trade_parameters = []
    # DEFINE CLOSE CONDITIONS
    for _entry in _open_entries:
        data_point = res_df.loc[_entry]
        new_parameter = [data_point['close']]
        new_df = res_df[_entry:].copy()
        close_entry = new_df[new_df['ema_20'] >
                             new_df['sma_10']].iloc[0]
        new_parameter.append(close_entry['close'])
        new_parameter.append(_entry)
        new_parameter.append(close_entry.name)
        trade_parameters.append(new_parameter)
    LOGGER.debug(f"got {len(trade_parameters)} trade parameters")
    for open_pr, close_pr, open_date, close_date in trade_parameters:
        # DEFINE MODE AND VOLUME
        trade = account.open_trade(CURRENCY.EURUSD, MODE.buy, 0.01,
                                   open_pr)
        trade.open_price = open_pr
        trade.close_price = close_pr
        trade.open_datetime = open_date
        trade.close_datetime = close_date
        account.close_trade(trade.trade_id, close_pr)
    LOGGER.debug("setup trades")
    trades_evaluated = account.evaluate_trades()
    LOGGER.debug("evaluated trades")
    LOGGER.debug("=======  STATISTICS =======")
    LOGGER.debug(f"Period analyzed: from {trade_parameters[0][-1]} to "
                 f"{trade_parameters[-1][-1]}")
    LOGGER.debug(f"profit = {account.balance - account.initial_balance}")
    profit_list = [trade.profit for trade in trades_evaluated]
    LOGGER.debug(f"Max profit at once: {max(profit_list)}")
    LOGGER.debug(f"Min profit at once: {min(profit_list)}")
    LOGGER.debug(f"Mean of profits: {sum(profit_list) / len(profit_list)}")
    # save a dataframe for later analysis
    pickle_arguments = [[tr.open_datetime, tr.close_datetime, tr.open_price,
                         tr.close_price, tr.profit, tr.new_balance] for tr in
                        trades_evaluated]
    pickle_df = pd.DataFrame({
        'open_datetime': [x[0] for x in pickle_arguments],
        'close_datetime': [x[1] for x in pickle_arguments],
        'open_price': [x[2] for x in pickle_arguments],
        'close_price': [x[3] for x in pickle_arguments],
        'profit': [x[4] for x in pickle_arguments],
        'balance': [x[5] for x in pickle_arguments]
    }).set_index('open_datetime')
    file_path = os.path.join(
        OUTER_FOLDER_PATH, "profit_dataframe.pickle")
    with open(file_path, 'wb') as f:
        pickle.dump(pickle_df, f, pickle.HIGHEST_PROTOCOL)
    LOGGER.debug("File pickle dumped")


if __name__ == "__main__":
    test_SMA_Simulation()
