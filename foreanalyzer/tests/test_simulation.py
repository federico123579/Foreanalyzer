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
    indicators = [{
        'name': 'SMA',
        'args': {'period': 12, 'timeframe': 3600}
    }]
    algo = BaseAlgorithm('TestAlgo', indicators)
    account = Account(1000)
    LOGGER.debug("components inited")
    algo.setup()
    account.setup()
    LOGGER.debug("components setup")
    df = algo.dataframes[CURRENCY.EURUSD].dataframe
    sma = algo.dataframes[CURRENCY.EURUSD].SMA
    LOGGER.debug("got df and sma")
    res_df = df.resample('3600S').asfreq()
    res_sma = sma.values.resample('3600S').asfreq()
    res_df['sma'] = res_sma
    res_df.dropna(inplace=True)
    LOGGER.debug(f"resampled & merged sma and dataframe to {len(res_df)}")
    _open_entries = res_df[res_df['close'] + 0.003 < res_df['sma']].index
    LOGGER.debug(f"got {len(_open_entries)} open entries")
    trade_parameters = []
    for _entry in _open_entries:
        data_point = res_df.loc[_entry]
        new_parameter = [data_point['close']]
        new_df = res_df[data_point.name:].copy()
        new_parameter.append(new_df[new_df['close'] >
                                    new_df['sma']].iloc[0]['close'])
        new_parameter.append(data_point.name)
        trade_parameters.append(new_parameter)
    LOGGER.debug(f"got {len(trade_parameters)} trade parameters")
    for open_pr, close_pr, close_date in trade_parameters:
        trade = account.open_trade(CURRENCY.EURUSD, MODE.buy, 0.01,
                                   open_pr)
        trade.datetime = close_date
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
    pickle_arguments = [[tr.datetime, tr.profit, tr.new_balance] for tr in
                        trades_evaluated]
    pickle_df = pd.DataFrame({
        'datetime': [x[0] for x in pickle_arguments],
        'profit': [x[1] for x in pickle_arguments],
        'balance': [x[2] for x in pickle_arguments]
    }).set_index('datetime')
    file_path = os.path.join(
        OUTER_FOLDER_PATH, "profit_dataframe.pickle")
    with open(file_path, 'wb') as f:
        pickle.dump(pickle_df, f, pickle.HIGHEST_PROTOCOL)
    LOGGER.debug("File pickle dumped")


if __name__ == "__main__":
    test_SMA_Simulation()
