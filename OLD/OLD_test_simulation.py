"""
tests.test_simulation
~~~~~~~~~~~~~~~~~~

Test the simulation module.
"""

import logging
import os.path
import pickle

import pandas as pd

from foreanalyzer._internal_utils import (CURRENCY, MODE, OUTER_FOLDER_PATH,
                                          STATE)
from foreanalyzer.account import Account
from foreanalyzer.algo_modules.boll_bands_1 import BolligerBands1
from foreanalyzer.exceptions import FundsExhausted

LOGGER = logging.getLogger("foreanalyzer.tests.test_simulation")
logging.getLogger("XTBApi").setLevel(logging.ERROR)


def test_Simulation():
    algo = BolligerBands1()
    account = Account()
    LOGGER.debug(f"testing {algo.__class__.__name__} with an account of "
                 f"{account.balance} balance")
    LOGGER.debug("components inited")
    algo = algo._load_pickle_eff()
    LOGGER.debug(algo.status)
    algo.setup()
    account.setup()
    LOGGER.debug("components setup")
    for currency in algo.currencies:
        # DEFINE OPEN ENTRIES
        signals = algo.get_open_signals(currency)
        # DEFINE CLOSE CONDITIONS
        close_sig = algo.get_close_signals(currency, signals)
        # ? - testing new function
        # margin = account.api.get_margin_trade('EURUSD', 0.09)['margin']
        # signals = pd.DataFrame(data={'open': close_sig['open_datetime'], 'close': close_sig['close_datetime'], 
        #                              'margin': pd.Series(data=[margin for _ in range(len(close_sig))])})
        # file_path_test = os.path.join(
        #     OUTER_FOLDER_PATH, "test_new_function.pickle")
        # with open(file_path_test, 'wb') as f:
        #     pickle.dump(signals, f, pickle.HIGHEST_PROTOCOL)
        # return
        # ? - stop testing new function
    # EXECUTE LONG
    # TODO: remove width
    for open_date, close_date, open_pr, close_pr, mode in \
            close_sig.values:
        # DEFINE MODE AND VOLUME
        trade = account.open_trade(CURRENCY.EURUSD, MODE.buy if mode == 0 else
                                   MODE.sell, 0.1, open_pr)
        trade.open_price = open_pr
        trade.close_price = close_pr
        trade.open_datetime = open_date
        trade.close_datetime = close_date
        account.close_trade(trade.trade_id, close_pr)
    LOGGER.debug("setup trades")
    # PICKLE DUMP
    LOGGER.debug("dumping algo...")
    file_path_test = os.path.join(
        OUTER_FOLDER_PATH, "algo.pickle")
    with open(file_path_test, 'wb') as f:
        pickle.dump(algo, f, pickle.HIGHEST_PROTOCOL)
    LOGGER.debug("finished dumping")
    # END DUMP
    try:
        trades_evaluated = account.evaluate_trades()
    except FundsExhausted as e:
        LOGGER.error(e)
        trades_evaluated = [trade for trade in account.trades if trade.state ==
                            STATE.EVALUATED]
        trades_evaluated[-1].new_balance = 0
    LOGGER.debug("evaluated trades")
    LOGGER.debug("=======  STATISTICS =======")
    res_df = algo.dataframes[algo.currencies[0]].dataframe
    LOGGER.debug(f"Period analyzed: from {res_df.iloc[0].name} to "
                 f"{res_df.iloc[-1].name}")
    LOGGER.debug(f"profit = {account.balance - account.initial_balance}")
    profit_list = [trade.profit for trade in trades_evaluated]
    LOGGER.debug(f"Max profit at once: {max(profit_list)}")
    LOGGER.debug(f"Min profit at once: {min(profit_list)}")
    LOGGER.debug(f"Mean of profits: {sum(profit_list) / len(profit_list)}")
    # save a dataframe for later analysis
    # TODO: remove width
    pickle_arguments = [[tr.open_datetime, tr.close_datetime, tr.mode.value,
                         tr.open_price, tr.close_price, tr.profit,
                         tr.new_balance] for tr in
                        trades_evaluated]
    # TODO: remove width
    pickle_df = pd.DataFrame({
        'open_datetime': [x[0] for x in pickle_arguments],
        'close_datetime': [x[1] for x in pickle_arguments],
        'mode': [x[2] for x in pickle_arguments],
        'open_price': [x[3] for x in pickle_arguments],
        'close_price': [x[4] for x in pickle_arguments],
        'profit': [x[5] for x in pickle_arguments],
        'balance': [x[6] for x in pickle_arguments]
    }).set_index('open_datetime')
    file_path_1 = os.path.join(
        OUTER_FOLDER_PATH, "profit_dataframe.pickle")
    file_path_2 = os.path.join(
        OUTER_FOLDER_PATH, "algo.pickle")
    # dumping analysis
    with open(file_path_1, 'wb') as f:
        pickle.dump(pickle_df, f, pickle.HIGHEST_PROTOCOL)
    # dumping algo
    with open(file_path_2, 'wb') as f:
        pickle.dump(algo, f, pickle.HIGHEST_PROTOCOL)
    LOGGER.debug("File pickle dumped")


if __name__ == "__main__":
    test_Simulation()
