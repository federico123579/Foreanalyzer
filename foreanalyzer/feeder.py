# ~~~~ feeder.py ~~~~
# forenalyzer.feeder
# ~~~~~~~~~~~~~~~~~~~

from abc import ABC, abstractmethod
import os
import zipfile

import pandas as pd

from foreanalyzer.console import CliConsole
import foreanalyzer.cache_optimization as opt
from foreanalyzer.globals import ACCEPTED_INSTRUMENTS
from foreanalyzer.exceptions import InstrumentNotListed


# ~ * LOGGER * ~
LOGGER = CliConsole()
LOGGER.prefix = "feeder"


# ~~~ * HIGH LEVEL CLASSES * ~~~
# TODO: add Feeder objects from zip file and from api
class Feeder(ABC):
    """Abstract class for feeding the plot/chart object with data"""
    def __init__(self, instrument: str):
        if instrument in ACCEPTED_INSTRUMENTS:
            self.instrument = instrument
        else:
            raise InstrumentNotListed(instrument)
    
    @abstractmethod
    def process_dataframe(self):
        pass


class ZipFeeder01(Feeder):
    """Feeder from zip files with precise instructions"""
    def __init__(self, instrument):
        super().__init__(instrument)
        self.feeder_id = 'ZIPF01'
        self.full_id = self.feeder_id + '-' + instrument

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
            LOGGER.debug(f"{self.instrument} already unzipped", 3)
            return basename + '.csv'
        else:
            zip_file = zipfile.ZipFile(filename, 'r')
            zip_file.extractall(new_folder)
            zip_file.close()
            os.rename(basename + '.txt', basename + '.csv')
            LOGGER.debug(f"{self.instrument} unzipped", 2)
            return basename + '.csv'

    def process_dataframe(self):
        filepath = opt.cache_path(['feeders'], [self.feeder_id, self.instrument])
        if os.path.isfile(filepath):
            LOGGER.debug(f"{self.full_id} cache found", 2)
            df = opt.load_cache(filepath)
        else:
            LOGGER.debug(f"{self.full_id} cache NOT found", 2)
            LOGGER.debug("processing")
            unzipped_filepath = self._unzip_data()
            df = pd.read_csv(unzipped_filepath)
            # ~~~ fix datetime and drop other columns ~~~
            LOGGER.debug("starting standardization...", 3)
            df.rename(columns=lambda x: x.strip('<>').lower(), inplace=True)
            timestamp = pd.Series(
                df['dtyyyymmdd'].map(str) + df['time'].map(str).apply(
                    lambda x: (6 - len(x)) * '0') + df['time'].map(str))
            df.insert(0, 'datetime', timestamp.map(pd.Timestamp))
            df.drop(columns=['ticker', 'vol', 'dtyyyymmdd', 'time'], inplace=True)
            df.set_index('datetime', inplace=True)
            # ~~~ * ~~~
            LOGGER.debug(f"dataframe normalised")
            opt.save_cache(filepath, df)
        return df
