# ~~~~ plot_handler.py ~~~~
# forenalyzer.plot_handler
# ~~~~~~~~~~~~~~~~~~~~~~~~~

from abc import ABC

import pandas as pd

from foreanalyzer.console import CliConsole


# ~ * LOGGER * ~
LOGGER = CliConsole()
LOGGER.prefix = "plot_handler"


# ~~~ * HIGH LEVEL CLASSES * ~~~
# column names present:
# close, datatime, high, low, open
class AbsPlotHandler(ABC):
    """abstract implementation of a Plot Handler
    object with the purpose of converting a dataset of values in different
    charts and plots (Candlestick and Kaji for the moment)
    ~~~~ * PARAMETERS * ~~~~
    * _columns: a list of columns to check in input dataframe
    * data: dataframe chart/plot, must be a called excpetion
    NotImplementedError untile the self.process method is called
    ~~~~ * METHODS * ~~~~
    * process: execution of the main converting process, just because the real
    process of dataframe manipulation can be long and may be timed with a
    progressbar.
    ~~~~ * INPUT * ~~~~
    takes a dataframe with columns exactly datetime|price"""
    def init(self):
        self._columns = list
        self.data = pd.DataFrame()


class CandlestickHandler(AbsPlotHandler):
    """handler for Candelstick charts/plots
    takes AbsPlotHandler as parent abstract class
    ~~~~ * PARAMETERS * ~~~~
    * _columns: (datetime, open, close, high, low)
    * timeframe: timeframe of the Chart (check if accepted in globals.py
    ~~~~ * INPUT * ~~~~
    takes a dataframe as input or check if the current input has the
    right columns."""
    def __init__(self, input_dataframe, timeframe):
        super().__init__(self)
        self._input_dataframe = input_dataframe
        # TODO: add accepted timeframes and conversion to globals
        self.timeframe = timeframe
    
    def plot(self):
        """plot the chart with data and process the Dataframe"""
        

class KajiHandler(AbsPlotHandler):
    """handler for a kaji chart
    takes AbsPlotHandler as parent abstract class
    ~~~~ * INPUT * ~~~~
    takes a dataframe as input or check if the current input is already a kaji
    input"""
    raise NotImplementedError


# ~~~ * LOV LEVEL UTILY FUNCTIONS * ~~~
def check_existing_chart(input_dataframe, columns_to_check):
    """check if columns_to_check are in the input_dataframe
    ~~~~ * INPUT & OUTPUT * ~~~~
    input_dataframe: a dataframe input of PlotHandler
    columns_to_check: a list of labels of columns, this will be compared with
    the list in the _columns parameter."""
    raise NotImplementedError


def set_datetime_index(input_dataframe):
    """set datetime columns given by a feeder as index in chart"""
    raise NotImplementedError