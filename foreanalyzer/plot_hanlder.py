# ~~~~ plot_handler.py ~~~~
# forenalyzer.plot_handler
# ~~~~~~~~~~~~~~~~~~~~~~~~~

from abc import ABC
import os.path

import pandas as pd

import foreanalyzer.cache_optimization as cache
from foreanalyzer.console import CliConsole
from foreanalyzer.feeder import FeederFactory
import foreanalyzer.globals as glob
import foreanalyzer.indicator as indi


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "plot_handler"

def DEBUG(text):
    LOGGER().debug(text, PREFIX)


# ~~~ * HIGH LEVEL CLASSES * ~~~
# column names present:
# close, datatime, high, low, open
# ~ * NEW PLOT CHECKLIST * ~
# [ ] add to globals
# [ ] add supported feeders to globals
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
    def __init__(self, plotter_id):
        self.plotter_id = plotter_id
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
    # TODO: fix arguments order
    def __init__(self, instruments: list, feeders: list, timeframe, **kwargs):
        super().__init__('CDSPLT')
        self.instruments = instruments
        # TODO: add accepted timeframes and conversion to globals
        if timeframe not in glob.ACCEPTED_TIMEFRAMES:
            raise ValueError(f"timeframe {timeframe} not accepted for {self.plotter_id}")
        if 'XTBF01' in feeders and 'time_past' not in [k for k in kwargs.keys()]:
            self._xtb_time_past = None
        else:
            self._xtb_time_past = kwargs['time_past']
        self.timeframe = timeframe
        self._supported_feeders = glob.SUPPORTED_FEEDERS[self.plotter_id]
        if not all([f in self._supported_feeders for f in feeders]):
            LOGGER().error(f"{[f for f in feeders if f not in self._supported_feeders]} not" +
                         "supported, ignoring these...", PREFIX)
        self.feeders = [[f, FeederFactory[f]] for f in feeders if f in self._supported_feeders]
        self.data = {instr: {f: None for f in [f for f, _ in self.feeders]} for instr in self.instruments}

    def feed(self): 
        """init & starts feeders then refines data received to meet the requisites of the
        plotter"""
        # DEFINING RESAMPLER
        def _resampler(input):
            if len(input) == 0:
                return None
            else:
                if input.name == "open":
                    return input[0]
                elif input.name == "close":
                    return input[-1]
                elif input.name == "high":
                    return max(input)
                elif input.name == "low":
                    return min(input)
                else:
                    return input[-1]
        # FEED main function
        for instr in self.instruments:
            DEBUG(f"feeding {self.plotter_id} with {instr}")
            for feeder_id, _feeder in self.feeders:
                DEBUG(f"current feeding {feeder_id}")
                if feeder_id == 'ZIPF01':
                    feeder = _feeder(instr)
                    feeder.setup()
                    df = feeder.process_dataframe()
                    feeder.shutdown()
                    # cache optimization
                    filepath = cache.cache_path(
                        ['plotters', self.plotter_id, feeder_id],
                        [instr, 'Rv1', f"{self.timeframe}S"])
                    if os.path.isfile(filepath):
                        df = cache.load_cache(filepath)
                    else:
                        # resampling
                        DEBUG(f"resampling {feeder_id} for {instr} with {self.timeframe}S")
                        df = df.resample(f"{self.timeframe}S").apply(_resampler).dropna()
                        cache.save_cache(filepath, df)
                    self.data[instr][feeder_id] = df
                elif feeder_id == 'XTBF01':
                    if self._xtb_time_past is None:
                        self._xtb_time_past = 3600*24*30*5
                    feeder = _feeder(instr, self.timeframe, self._xtb_time_past)
                    feeder.setup()
                    df = feeder.process_dataframe()
                    feeder.shutdown()
                    self.data[instr][feeder_id] = df
                else:
                    LOGGER().error(f"{feeder_id} not fully supported for {self.plotter_id}", PREFIX)
        return self.data
    
    def add_indicator(self, name_indicator, *args, **kwargs):
        """add indicator and process it if supported"""
        if name_indicator in glob.SUPPORTED_INDICATORS:
            for instr in self.instruments:
                for feeder_id, _ in self.feeders:
                    df = self.data[instr][feeder_id]
                    df = indi.IndicatorFactory[name_indicator](df, *args, **kwargs)
        else:
            raise ValueError(f"{name_indicator} not supported")
        

class KajiHandler(AbsPlotHandler):
    """handler for a kaji chart
    takes AbsPlotHandler as parent abstract class
    ~~~~ * INPUT * ~~~~
    takes a dataframe as input or check if the current input is already a kaji
    input"""
    pass


# ~~~ * LOV LEVEL UTILY FUNCTIONS * ~~~
def check_existing_chart(input_dataframe, columns_to_check):
    """check if columns_to_check are in the input_dataframe
    ~~~~ * INPUT & OUTPUT * ~~~~
    input_dataframe: a dataframe input of PlotHandler
    columns_to_check: a list of labels of columns, this will be compared with
    the list in the _columns parameter."""
    pass


def set_datetime_index(input_dataframe):
    """set datetime columns given by a feeder as index in chart"""
    pass


# ~ * FACTORY * ~
PlotterFactory = {
    'CDSPLT': CandlestickHandler
}