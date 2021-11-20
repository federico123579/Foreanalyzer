# ~~~~ algo.py ~~~~
# forenalyzer.algo
# ~~~~~~~~~~~~~~~~~

from abc import ABCMeta, abstractmethod

import pandas as pd

from foreanalyzer.console import CliConsole
from foreanalyzer.plot_hanlder import PlotterFactory


# ~ * LOGGER * ~
LOGGER = CliConsole
PREFIX = "algo"

def DEBUG(text, level=1):
    LOGGER().debug(text, PREFIX, level)

def INFO(text):
    LOGGER().info(text, PREFIX)

def WARN(text):
    LOGGER().warn(text, PREFIX)

def ERROR(text):
    LOGGER().error(text, PREFIX)


# ~~~ * HIGH LEVEL CLASSES * ~~~
class BaseAlgorithm(metaclass=ABCMeta):
    """basic implementation of algortihm
    ~ Arguments ~
    * open_long_trades_on: indicate the open price of a long order
    * open_short_trades_on: indicate the open price of a short order
    * close_long_trades_on: indicate the close price of a long order
    * close_short_trades_on: indicate the close price of a short order
    * open_long_trades_on: indicate if open_long are set on a previous row
    * enter_short_on_previous_row: indicate if open_short are set on a previous row
    * exit_long_on_previous_row: indicate if close_long are set on a previous row
    * exit_short_on_previous_row: indicate if close_short are set on a previous row
    * volume_of_trade: margin money spent on trade
    * stop_loss: stop loss with profit"""
    def __init__(self, algo_id,
                 n_previous_rows_to_check=1,
                 volume=300,
                 stop_loss=None):
        self._id = algo_id
        self.process_config = {
            'n_prev_rows': n_previous_rows_to_check,
            'volume': volume,
            'stop_loss': stop_loss
        }
        self.status = {
            'plot': 0 # 0 not plotted - 1 plotted
        }
        self.data = None
        self.trades = None

    @abstractmethod
    def check_close_long(self, open_row, row, rows):
        """get row and return check then this will be in a for loop"""

    @abstractmethod
    def check_close_short(self, open_row, row, rows):
        """get row and return check then this will be in a for loop"""

    @abstractmethod
    def check_open_long(self, row, rows):
        """look above, same a check close but with open"""

    @abstractmethod
    def check_open_short(self, row, rows):
        """look above, same a check close but with open"""

    @abstractmethod
    def plot(self):
        """feed and plot chart"""

    def process(self):
        """process data and get trades"""
        if self.status['plot'] == 0:
            ERROR("plot required, plotting now")
            self.plot()
        df0 = self.data.copy()
        df0 = df0.reset_index()
        # set process flags
        trade_open = False
        type_of_trade = None
        # init collection of trade data
        long_trades_gains = pd.DataFrame()
        short_trades_gains = pd.DataFrame()
        long_datetime_open = []
        long_datetime_close = []
        long_price_open = []
        long_price_close = []
        short_datetime_open = []
        short_datetime_close = []
        short_price_open = []
        short_price_close = []
        # check every row in self.data set by self.plot
        for index, row in df0.iterrows():
            # set a precedent row to compare in check functions
            if index-self.process_config['n_prev_rows'] < 0:
                continue
            rows_to_check = df0.iloc[index-self.process_config['n_prev_rows']:index+1]
            # if there isn't any trade open look for the right condition to open it
            if not trade_open:
                # set long condition
                opened_long = self.check_open_long(row, rows=rows_to_check)
                # set short condition
                opened_short = self.check_open_short(row, rows=rows_to_check)
                # if either one on the two is correct then open trade
                if opened_long != False or opened_short != False:
                    # set flag so then this will check close and not open
                    trade_open = True
                    if opened_long != False:
                        # set type of trade
                        type_of_trade = 'long'
                        # append datetime of open
                        long_datetime_open.append(row['datetime'])
                        # find the open price
                        long_price_open.append(opened_long)
                    elif opened_short != False:
                        # set type of trade
                        type_of_trade = 'short'
                        # append datetime of open
                        short_datetime_open.append(row['datetime'])
                        # find the open price
                        short_price_open.append(opened_short)
            # if trade is already opened check for closes
            elif trade_open:
                # if last order is long look for long close conditions
                if type_of_trade == 'long':
                    closed_long = self.check_close_long(open_row=self.data.loc[long_datetime_open[-1]], row=row, rows=rows_to_check)
                    # check if stop loss is applied
                    if self.process_config['stop_loss'] != None:
                        if closed_long != False or temp_profit < self.process_config['stop_loss']:
                            if temp_profit < self.process_config['stop_loss']:
                                close_price = row['close']
                            elif closed_long != False:
                                close_price = closed_long
                            # NOTE: this works only for EURUSD
                            temp_profit = (((close_price - long_price_open[-1]) - 0.00009) * self.process_config['volume'] * 33)
                            long_datetime_close.append(row['datetime'])
                            long_price_close.append(close_price)
                            # set trade closed and look for a new trade
                            trade_open = False
                    elif closed_long:
                        close_price = closed_long
                        long_datetime_close.append(row['datetime'])
                        long_price_close.append(close_price)
                        # set trade closed and look for a new trade
                        trade_open = False
                elif type_of_trade == 'short':
                    closed_short = self.check_close_short(open_row=self.data.loc[short_datetime_open[-1]], row=row, rows=rows_to_check)
                    # check if stop loss is applied
                    if self.process_config['stop_loss'] != None:
                        if closed_short != False or temp_profit < self.process_config['stop_loss']:
                            if temp_profit < self.process_config['stop_loss']:
                                close_price = row['close']
                            elif closed_short != False:
                                close_price = closed_short
                            # NOTE: this works only for EURUSD
                            temp_profit = (((long_price_open[-1] - close_price) - 0.00009) * self.process_config['volume'] * 33)
                            short_datetime_close.append(row['datetime'])
                            short_price_close.append(close_price)
                            # set trade closed and look for a new trade
                            trade_open = False
                    elif closed_short:
                        close_price = closed_short
                        short_datetime_close.append(row['datetime'])
                        short_price_close.append(close_price)
                        # set trade closed and look for a new trade
                        trade_open = False
        # merge all data
        # long trades
        long_trades_gains['open_dt'] = pd.Series(long_datetime_open)
        long_trades_gains['close_dt'] = pd.Series(long_datetime_close)
        long_trades_gains['open_price'] = pd.Series(long_price_open)
        long_trades_gains['close_price'] = pd.Series(long_price_close)
        long_trades_gains['mode'] = pd.Series([0 for _ in range(len(long_datetime_open))])
        long_trades_gains['profit'] = ((long_trades_gains['close_price'] - long_trades_gains[
            'open_price']) - 0.00009) * self.process_config['volume'] * 33
        long_trades_gains = long_trades_gains.dropna()
        # short trades
        short_trades_gains['open_dt'] = pd.Series(short_datetime_open)
        short_trades_gains['close_dt'] = pd.Series(short_datetime_close)
        short_trades_gains['open_price'] = pd.Series(short_price_open)
        short_trades_gains['close_price'] = pd.Series(short_price_close)
        short_trades_gains['mode'] = pd.Series([1 for _ in range(len(short_datetime_open))])
        short_trades_gains['profit'] = ((short_trades_gains['open_price'] - short_trades_gains[
            'close_price']) - 0.00009) * self.process_config['volume'] * 33
        short_trades_gains = short_trades_gains.dropna()
        self.trades = pd.concat([long_trades_gains, short_trades_gains])
        return self.trades

    def get_result(self, gains):
        df0 = self.data
        # statistics
        day_profits = gains.drop(columns=['open_price', 'close_price', 'close_dt', 'mode']).set_index('open_dt').resample('86400S').aggregate(sum)
        month_profits = gains.drop(columns=['open_price', 'close_price', 'close_dt', 'mode']).set_index('open_dt').resample(f'{86400*30}S').aggregate(sum)
        win_rate = len(gains[gains['profit'] > 0]) / len(gains) * 100
        day_profit_mean = day_profits.values.mean()
        month_profit_mean = month_profits.values.mean()
        days_traded = len(day_profits[day_profits['profit'] != 0]) / len(df0.resample('86400S').asfreq().values) * 100
        average_win = gains['profit'].mean()
        average_positive_profit = gains[gains['profit'] > 0]['profit'].mean()
        average_negative_profit = gains[gains['profit'] < 0]['profit'].mean()
        sum_profit = gains['profit'].sum()
        CliConsole().write(f"N trasn: {len(gains)}\nwin ratio: {win_rate:.2f}%\nwin/loss: " +
            f"{abs(average_positive_profit/average_negative_profit)*100:.2f}%" +
            f"\naverage win: {average_win:.4f}\navg positive: {average_positive_profit:.4f}" +
            f"\navg negative: {average_negative_profit:.4f}\nsum: {sum_profit:.2f}" +
            f"\nday profit mean: {day_profit_mean:.4f}\nmonth profit mean: {month_profit_mean:.2f}" +
            f"\ndays on percentage: {days_traded:.2f}%\nmonthly gain: {month_profit_mean/self.process_config['volume']*100:.2f}% " +
            f"- {self.process_config['volume']*(month_profit_mean/self.process_config['volume']+1):.2f}\nannual gain: {(month_profit_mean/self.process_config['volume']+1)**12*100:.2f}% - " +
            f"{self.process_config['volume']*(month_profit_mean/self.process_config['volume']+1)**12:.2f}")
    
    def get_score(self, gains):
        month_profits = gains.drop(columns=['open_price', 'close_price', 'close_dt', 'mode']).set_index('open_dt').resample(f'{86400*30}S').aggregate(sum)
        month_profit_mean = month_profits.values.mean()
        monthly_gain = month_profit_mean/self.process_config['volume']*100
        INFO(f"score of {monthly_gain:.2f}% and monthly of {month_profit_mean:.2f}")
        return monthly_gain          

class ATS03(BaseAlgorithm):
    def __init__(self):
        super().__init__(
            algo_id='ATS03',
            n_previous_rows_to_check=1,
            volume=300)
        self.plotter = PlotterFactory['CDSPLT'](
            instruments=['EURUSD'],
            feeders=['XTBF01'],
            timeframe=1800,
            time_past=60*60*24*30*6)
    
    def plot(self):
        if self.status['plot'] == 1:
            WARN("plot already given")
        self.plotter.feed()
        self.plotter.add_indicator('BBANDS', period=20)
        self.plotter.add_indicator('RSI', period=14)
        self.plotter.add_indicator('EMA', period=180)
        self.plotter.add_indicator('EMA', period=365)
        PIP = 0.0001
        self.plotter.add_indicator('SR_LV', retest=2, tolerance=5*PIP)
        self.status['plot'] = 1
        self.data = self.plotter.data['EURUSD']['XTBF01']
        DEBUG(f"{self._id} plotted")
        return self.data
    
    def check_close_long(self, open_row, row, rows):
        """get row and return check then this will be in a for loop"""
        if row['high'] > open_row['SUP_LV_2']:
            return open_row['SUP_LV_2']
        elif row['low'] < open_row['RES_LV_2']:
            return open_row['RES_LV_2']
        else:
            return False

    def check_close_short(self, open_row, row, rows):
        """get row and return check then this will be in a for loop"""
        if row['low'] < open_row['RES_LV_2']:
            return open_row['RES_LV_2']
        elif row['high'] > open_row['SUP_LV_2']:
            return open_row['SUP_LV_2']
        else:
            return False

    def check_open_long(self, row, rows):
        """look above, same a check close but with open"""
        previous_row = rows.iloc[-2]
        first_condition = previous_row['RSI_14'] < 30
        second_condition = row['low'] < previous_row['BBANDS_20_dw']
        third_condition = previous_row['EMA_180'] > previous_row['EMA_365']
        if first_condition and second_condition and third_condition:
            return previous_row['BBANDS_20_dw']
        else:
            return False

    def check_open_short(self, row, rows):
        """look above, same a check close but with open"""
        previous_row = rows.iloc[-2]
        first_condition = previous_row['RSI_14'] > 70
        second_condition = row['high'] > previous_row['BBANDS_20_up']
        third_condition = previous_row['EMA_180'] < previous_row['EMA_365']
        if first_condition and second_condition and third_condition:
            return previous_row['BBANDS_20_up']
        else:
            return False  


class ATS02(BaseAlgorithm):
    def __init__(self):
        super().__init__(
            algo_id='ATS02',
            open_long_trades_on='',
            open_short_trades_on='',
            close_long_trades_on='',
            close_short_trades_on='',
            enter_long_on_previous_row=True,
            enter_short_on_previous_row=True,
            exit_long_on_previous_row=True,
            exit_short_on_previous_row=True,
            n_previous_rows_to_check=10,
            volume=300)
        self.plotter = PlotterFactory['CDSPLT'](
            instruments=['EURUSD'],
            feeders=['XTBF01'],
            timeframe=300,
            time_past=60*60*24*7)
    
    def plot(self):
        if self.status['plot'] == 1:
            WARN("plot already given")
        self.plotter.feed()
        self.add_indicator('EMA', period=21)
        self.add_indicator('EMA', period=13)
        self.add_indicator('EMA', period=9)
        self.status['plot'] = 1
        self.data = self.plotter.data['EURUSD']['XTBF01']
        DEBUG(f"{self._id} plotted")
        return self.data
    
    def check_close_long(self, row, previous_row, rows):
        """get row and return check then this will be in a for loop"""

    def check_close_short(self, row, previous_row, rows):
        """get row and return check then this will be in a for loop"""

    def check_open_long(self, row, previous_row, rows):
        """look above, same a check close but with open"""
        for y in range(1,6):
            first_phase = rows[-7-y:-1-y]
            first_candle = rows[-1-y]
            second_phase = rows[-y:]
            # first phase check
            check = True
            for ema in ['EMA_9', 'EMA_13', 'EMA_21']:
                if not (all(first_phase['open'] > first_phase[ema]) and all(
                        first_phase['close'] > first_phase[ema])):
                    check = False
                # first candle
                if not (first_candle['open'] < first_candle[ema] or first_candle['close'] < first_candle[ema]):
                    check = False
            if not check:
                continue
            # else continue
            joined_first_phase = rows[-7-y:-y]
            up_level = max(max([x['open'] for x in joined_first_phase]), max([x['close'] for x in joined_first_phase]))
            down_level = min(min([x['open'] for x in joined_first_phase]), min([x['close'] for x in joined_first_phase]))
            # second phase check
            if not all([x['low'] > down_level for x in second_phase]):
                continue
            if row['high'] > up_level:
                return True
            else:
                continue
        return False

    def check_open_short(self, row, previous_row, rows):
        """look above, same a check close but with open"""
        for y in range(1,6):
            first_phase = rows[-7-y:-1-y]
            first_candle = rows[-1-y]
            second_phase = rows[-y:]
            # first phase check
            check = True
            for ema in ['EMA_9', 'EMA_13', 'EMA_21']:
                if not (all(first_phase['open'] < first_phase[ema]) and all(
                        first_phase['close'] < first_phase[ema])):
                    check = False
                # first candle
                if not (first_candle['open'] > first_candle[ema] or first_candle['close'] > first_candle[ema]):
                    check = False
            if not check:
                continue
            # else continue
            joined_first_phase = rows[-7-y:-y]
            up_level = max(max([x['open'] for x in joined_first_phase]), max([x['close'] for x in joined_first_phase]))
            down_level = min(min([x['open'] for x in joined_first_phase]), min([x['close'] for x in joined_first_phase]))
            # second phase check
            if not all([x['high'] < up_level for x in second_phase]):
                continue
            if row['low'] < down_level:
                return True
            else:
                continue
        return False


class ATS01(BaseAlgorithm):
    """ ~ CATEGORY
    A - Algorithm
    TS - Test
    01 - serial"""
    def __init__(self):
        super().__init__(
            algo_id='ATS01')
        self.plotter = PlotterFactory['CDSPLT'](
            instruments=['EURUSD'],
            feeders=['ZIPF01'],
            timeframe=1800,
            time_past=24*60*60*12)
    
    def plot(self, instr='EURUSD', feed='ZIPF01'):
        """feed and plot chart"""
        if self.status['plot'] == 1:
            WARN("plot already given")
        self.plotter.feed()
        self.plotter.add_indicator('BBANDS', period=30)
        self.plotter.add_indicator('SMA', period=5)
        self.plotter.add_indicator('SMA', period=20)
        self.plotter.add_indicator('SMA', period=50)
        self.plotter.add_indicator('SMA', period=100)
        self.plotter.add_indicator('SMA', period=200)
        self.status['plot'] = 1
        self.data = self.plotter.data[instr][feed]
        DEBUG(f"{self._id} plotted")
        return self.data
    
    def process(self, vol=300):
        """process data and get trades"""
        if self.status['plot'] == 0:
            ERROR("plot required, plotting now")
            self.plot()
        self.data = self.data[(self.data.index.year == 2018)].resample('1800S').asfreq()
        #self.data = self.data.resample('1800S').asfreq()
        hr6_df = self.plotter.resample_data(self.data, 60*60*6)
        hr12_df = self.plotter.resample_data(self.data, 60*60*12)
        d1_df = self.plotter.resample_data(self.data, 60*60*24)
        d3_df = self.plotter.resample_data(self.data, 60*60*24*3)
        d7_df = self.plotter.resample_data(self.data, 60*60*24*7)
        self.data['6HR_HG'] = hr6_df['high'].resample('1800S').bfill()
        self.data['12HR_HG'] = hr12_df['high'].resample('1800S').bfill()
        self.data['1D_HG'] = d1_df['high'].resample('1800S').bfill()
        self.data['3D_HG'] = d3_df['high'].resample('1800S').bfill()
        self.data['7D_HG'] = d7_df['high'].resample('1800S').bfill()
        self.data['6HR_LW'] = hr6_df['low'].resample('1800S').bfill()
        self.data['12HR_LW'] = hr12_df['low'].resample('1800S').bfill()
        self.data['1D_LW'] = d1_df['low'].resample('1800S').bfill()
        self.data['3D_LW'] = d3_df['low'].resample('1800S').bfill()
        self.data['7D_LW'] = d7_df['low'].resample('1800S').bfill()
        self.data.dropna(inplace=True)
        DEBUG("resistance and support levels set")
        STOP_LOSS = -300
        # get data
        df0 = self.data.copy()
        df0 = df0.reset_index()
        lg_gains = pd.DataFrame()
        sh_gains = pd.DataFrame()
        lg_odt = []
        lg_oprice = []
        lg_cdt = []
        lg_cprice = []
        sh_odt = []
        sh_oprice = []
        sh_cdt = []
        sh_cprice = []
        lg_profit = []
        sh_profit = []
        # check
        mode = 0
        for index, row in df0.iterrows():
            rowp = df0.iloc[index-1]
            if mode == 0:
                condition_long = (row['low'] < rowp['BBANDS_30_dw'] and rowp['close'] > rowp['SMA_50'])
                condition_short = (row['high'] > rowp['BBANDS_30_up'] and rowp['close'] < rowp['SMA_50'])
                if condition_long or condition_short:
                    if condition_long:
                        lg_odt.append(row['datetime'])
                        lg_oprice.append(rowp['BBANDS_30_dw'])
                        trans = 0
                    elif condition_short:
                        sh_odt.append(row['datetime'])
                        sh_oprice.append(rowp['BBANDS_30_up'])
                        trans = 1
                    mode = 1
            elif mode == 1:
                close_long_condition = row['high'] > rowp['BBANDS_30_md']
                close_short_condition = row['low'] < rowp['BBANDS_30_md']
                if trans == 0:
                    lg_temp_profit = (((row['low'] - lg_oprice[-1]) - 0.00009) * vol * 33)
                    if (close_long_condition or lg_temp_profit < STOP_LOSS):
                        if lg_temp_profit < STOP_LOSS:
                            lg_cprice.append(row['low'])
                        else:
                            lg_cprice.append(row['BBANDS_30_md'])
                        lg_cdt.append(row['datetime'])
                        lg_profit.append(((lg_cprice[-1] - lg_oprice[-1]) - 0.00009) * vol * 33)
                        mode = 0
                elif trans == 1:
                    sh_temp_profit = ((-(row['high'] - sh_oprice[-1]) - 0.00009) * vol * 33)
                    if (close_short_condition or sh_temp_profit < STOP_LOSS):
                        if sh_temp_profit < STOP_LOSS:
                            sh_cprice.append(row['high'])
                        else:
                            sh_cprice.append(row['BBANDS_30_md'])
                        sh_cdt.append(row['datetime'])
                        sh_profit.append(((sh_oprice[-1] - sh_cprice[-1]) - 0.00009) * vol * 33)
                        mode = 0
        # set up dataframe
        # long
        lg_gains['open_dt'] = pd.Series(lg_odt)
        lg_gains['close_dt'] = pd.Series(lg_cdt)
        lg_gains['open_price'] = pd.Series(lg_oprice)
        lg_gains['close_price'] = pd.Series(lg_cprice)
        lg_gains['mode'] = pd.Series([0 for _ in range(len(lg_odt))])
        lg_gains['profit'] = pd.Series(lg_profit)
        lg_gains = lg_gains.dropna()
        # short
        sh_gains['open_dt'] = pd.Series(sh_odt)
        sh_gains['close_dt'] = pd.Series(sh_cdt)
        sh_gains['open_price'] = pd.Series(sh_oprice)
        sh_gains['close_price'] = pd.Series(sh_cprice)
        sh_gains['mode'] = pd.Series([1 for _ in range(len(lg_odt))])
        sh_gains['profit'] = pd.Series(sh_profit)
        sh_gains = sh_gains.dropna()
        gains = pd.concat([lg_gains, sh_gains])
        DEBUG("gains processed")
        return gains
    

# ~~~ * ALGO FACTORY * ~~~
AlgoFactory = {
    'ATS01': ATS01,
    'ATS02': ATS02,
    'ATS03': ATS03,
}