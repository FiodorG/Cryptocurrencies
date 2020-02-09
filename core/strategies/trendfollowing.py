import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .strategy import StrategyInterface
from ..utilities import utilities

pd.options.mode.chained_assignment = None


class TrendFollowing(StrategyInterface):

    def __init__(self, pairs, exchanges, strategy_parameters):
        """
        pairs = currency pairs on which the strategy is ran
        exchanges = exchanges on which the strategy is ran
        strategy_parameters = all strategy parameters
        """
        super(TrendFollowing, self).__init__(pairs, exchanges, strategy_parameters)
        self.exchange = exchanges[0]

        if len(self.exchanges) > 1:
            self.log.error('Trend Following only doable on one exchange at the moment.')
            raise ValueError('Only use one exchange.')

        if len(self.pairs) != 1:
            self.log.error('Trend Following only doable on one asset at the moment')
            raise ValueError('Only use one asset.')

    def get_data_for_backtest(self, data_location):
        return utilities.get_data_from_local(data_location, self.pairs[0])

    def clean_and_extend_data(self, data):
        first_time = datetime.datetime.strptime('2017-07-21 07:00:00.0000', "%Y-%m-%d %H:%M:%S.%f")
        data = data[data.datetime > first_time]

        data['close_return'] = data['close'].pct_change().fillna(0)
        data['close_ma20'] = data[['close']].ewm(halflife=20).mean()
        data['close_ma40'] = data[['close']].ewm(halflife=40).mean()
        data['close_ma20_minus_ma40'] = data['close_ma20'] - data['close_ma40']
        data['close_std20'] = data[['close']].ewm(halflife=20).std().fillna(0)
        data['close_std40'] = data[['close']].ewm(halflife=40).std().fillna(0)

        return data

    def compute_signal(self, data):
        """
        data = ohlc of the pairs
        """
        data['close_ma20_minus_ma40_cum'] = np.cumsum(data['close_ma20_minus_ma40'])
        signal = data['close_ma20_minus_ma40_cum'].tail(1).values[0]

        return {
            'signal': signal
        }

    def compute_pnl(self, data, stats_signal):
        """
        data = ohlc of the pairs
        stats_signal = signal and associated values
        """
        log_return = data['close'].tail(1).values[0]/data['close'].head(1).values[0] - 1
        if stats_signal['signal'] > self.strategy_parameters['crossover_value']:
            pnl = -log_return
        elif stats_signal['signal'] < -self.strategy_parameters['crossover_value']:
            pnl = log_return
        else:
            pnl = 0

        return {
            'pnl': pnl
        }

    def compute_stats(data, strategy_parameters):
        return {}

    def print_backtest_stats(self, data):
        data['cumpnl'] = np.cumprod(data['pnl'] + 1)
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(data.index, data.close, 'g-')
        ax2.plot(data.index, data.cumpnl, 'b-')
        ax1.set_ylabel('close', color='g')
        ax2.set_ylabel('pnl', color='b')
        plt.show()
