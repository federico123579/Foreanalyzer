# ~~~~ feeder.py ~~~~
# forenalyzer.feeder
# ~~~~~~~~~~~~~~~~~~~

from abc import ABC, abstractmethod
import os
import time
import zipfile

import pandas as pd

from foreanalyzer.api_handler import APIHandler
from foreanalyzer.console import CliConsole
import foreanalyzer.cache_optimization as opt
from foreanalyzer.globals import ACCEPTED_INSTRUMENTS
from foreanalyzer.exceptions import InstrumentNotListed


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "feeder"

def DEBUG(text, level=1):
    LOGGER().debug(text, PREFIX, level)


# ~~~ * HIGH LEVEL CLASSES * ~~~
class AbsFeeder(ABC):
    """Abstract class for feeding the plot/chart object with data"""
    def __init__(self, instrument: str, feeder_id, allow_cache=True):
        self._status = 0
        self.feeder_id = feeder_id
        self._allow_cache = allow_cache
        self.full_id = self.feeder_id + '-' + instrument
        if instrument in ACCEPTED_INSTRUMENTS:
            self.instrument = instrument
        else:
            raise InstrumentNotListed(instrument)
    
    def _setup(self):
        pass

    def setup(self, *args, **kwargs):
        """setup feeder, here go every action needed at the startup"""
        if self._status:
            DEBUG(f"{self.full_id} already setup", 3)
        else:
            self._setup(*args, **kwargs)
            self._status = 1
            DEBUG(f"{self.full_id} setup", 3)
    
    def _shutdown(self):
        pass
    
    def shutdown(self, *args, **kwargs):
        """clean & close procedure"""
        if not self._status:
            DEBUG(f"{self.full_id} already shutdown", 3)
        else:
            self._shutdown(*args, **kwargs)
            self._status = 0
            DEBUG(f"{self.full_id} shutdown", 3)

    @abstractmethod
    def _process(self):
        """then wrap with process_dataframe"""
        pass

    def _cache_instructions(self):
        """insert cache naming instructions"""
        return [self.feeder_id, self.instrument]

    def process_dataframe(self):
        """process dataframe anc cache manager"""
        if not self._status:
            LOGGER().warn(f"{self.full_id} - trying to process but not setup", PREFIX)
            self.setup()
        filepath = opt.cache_path(['feeders'], self._cache_instructions())
        if os.path.isfile(filepath):
            DEBUG(f"{self.full_id} cache found", 2)
            df = opt.load_cache(filepath)
        else:
            if self._allow_cache:
                DEBUG(f"{self.full_id} cache NOT found", 2)
            DEBUG("processing")
            df = self._process()
            # ~~~ * ~~~
            DEBUG(f"dataframe normalised")
            if self._allow_cache:
                opt.save_cache(filepath, df)
        return df


# ~ * NEW FEEDER CHECKLIST * ~
# [ ] add feeder support to plot in plot_hanlder
# [ ] add feeder support to plot in globals
class XTBFeeder01(AbsFeeder):
    """Feeder from XTB client communicating with an APIHandler"""
    def __init__(self, instrument, timeframe, time_past):
        super().__init__(instrument, 'XTBF01', False)
        self.timeframe = timeframe
        self.time_past = time_past

    def _setup(self):
        """start the connection with the client"""
        APIHandler().setup()
    
    def _shutdown(self):
        APIHandler().shutdown()
    
    def _cache_instructions(self):
        return [self.feeder_id, str(self.timeframe) + 'TF',
                str(self.time_past) + 'TP', self.instrument]
    
    def _process(self):
        raw_values = APIHandler().api.get_chart_last_request(
            self.instrument, self.timeframe // 60, time.time() - self.time_past)
        values = raw_values['rateInfos']
        datetimes = [pd.to_datetime(x['ctm'] / 1000, unit='s').tz_localize(
            'UTC').tz_convert('Europe/Berlin') for x in values]
        opens = [x['open'] / 10 ** raw_values['digits'] for x in values]
        closes = [(x['close'] + x['open']) / 10 ** raw_values['digits'] for x
                   in values]
        high = [(x['high'] + x['open']) / 10 ** raw_values['digits'] for x in
                 values]
        low = [(x['low'] + x['open']) / 10 ** raw_values['digits'] for x in
                values]
        df = pd.DataFrame(data={'datetime': datetimes, 'open': opens,
                                  'close': closes, 'high': high, 'low': low})
        df.set_index('datetime', inplace=True)
        return df


class ZipFeeder01(AbsFeeder):
    """Feeder from zip files with precise instructions"""
    def __init__(self, instrument):
        super().__init__(instrument, 'ZIPF01')

    def _unzip_data(self):
        """unzip data from folder data outside of foreanalyzer"""
        # find path
        folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        filename = os.path.join(folder, self.instrument + '.zip')
        new_folder = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.isdir(new_folder):
            os.mkdir(new_folder)
        # unzip file
        basename = os.path.join(new_folder, self.instrument)
        if os.path.isfile(basename + '.csv'):
            DEBUG(f"{self.instrument} already unzipped", 3)
            return basename + '.csv'
        else:
            zip_file = zipfile.ZipFile(filename, 'r')
            zip_file.extractall(new_folder)
            zip_file.close()
            os.rename(basename + '.txt', basename + '.csv')
            DEBUG(f"{self.instrument} unzipped", 2)
            return basename + '.csv'

    def _cache_instructions(self):
        return [self.feeder_id, self.instrument]

    def _process(self):
        unzipped_filepath = self._unzip_data()
        df = pd.read_csv(unzipped_filepath)
        # ~~~ fix datetime and drop other columns ~~~
        DEBUG("starting standardization...", 3)
        df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
        timestamp = pd.Series(
            df['dtyyyymmdd'].map(str) + df['time'].map(str).apply(
                lambda x: (6 - len(x)) * '0') + df['time'].map(str))
        df.insert(0, 'datetime', timestamp.map(pd.Timestamp))
        df.drop(columns=['ticker', 'vol', 'dtyyyymmdd', 'time'], inplace=True)
        df.set_index('datetime', inplace=True)
        return df


# ~~~ * FEEDER FACTORY * ~~~
FeederFactory = {
    'XTBF01': XTBFeeder01,
    'ZIPF01': ZipFeeder01
}