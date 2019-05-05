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
from foreanalyzer.algorithm import RealAlgorithm

LOGGER = logging.getLogger("foreanalyzer.tests.test_simulation")


def test_SMA_Simulation():
    algo = RealAlgorithm()
    account = Account(1000000)
    LOGGER.debug("components inited")
    algo.setup()
    account.setup()
    LOGGER.debug("components setup")
    df = algo.dataframes[CURRENCY.EURUSD].data
    LOGGER.debug("got data for later reindex")
    dates = algo.get_datetime_trades(CURRENCY.EURUSD)
    LOGGER.debug("got dates and now resample with trigger of act")
    list_trades = df.reindex(dates).resample('3600S').asfreq().dropna().index
    LOGGER.debug("got list of trades")
    sma = SMA(df, algo.dataframes[CURRENCY.EURUSD].SMA.period,
              algo.dataframes[CURRENCY.EURUSD].SMA.reducer.interval)
    sma.execute()
    close_dates = sma.execute_filter('above')
    LOGGER.debug("got close dates (of price below sma)")
    close_couples = []
    for trade in list_trades:
        open_date = trade
        if len(close_dates[trade < close_dates]) > 0:
            close_date = close_dates[trade < close_dates][0]
            close_couples.append(
                [df['close'].loc[open_date], df['close'].loc[close_date],
                 close_date])
    LOGGER.debug("got close couples")
    for open_pr, close_pr, close_date in close_couples:
        trade = account.open_trade(CURRENCY.EURUSD, MODE.buy, 0.01,
                                   open_pr)
        trade.datetime = close_date
        account.close_trade(trade.trade_id, close_pr)
    LOGGER.debug("setup trades")
    trades_evaluated = account.evaluate_trades()
    LOGGER.debug("evaluated trades")
    LOGGER.debug("=======  STATISTICS =======")
    LOGGER.debug(f"Period analyzed: from {list_trades[0]} to "
                 f"{list_trades[-1]}")
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
        OUTER_FOLDER_PATH, "data_analysis", "profit_dataframe.pickle")
    with open(file_path, 'wb') as f:
        pickle.dump(pickle_df, f, pickle.HIGHEST_PROTOCOL)
    LOGGER.debug("File pickle dumped")


if __name__ == "__main__":
    test_SMA_Simulation()
