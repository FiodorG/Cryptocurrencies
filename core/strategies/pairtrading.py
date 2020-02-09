import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from .strategy import StrategyInterface
from ..utilities import utilities

from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import Ridge
from pykalman import KalmanFilter
from sklearn.metrics import r2_score

pd.options.mode.chained_assignment = None


class PairTrading(StrategyInterface):

    def __init__(self, pairs, exchanges, strategy_parameters):
        """
        pairs = currency pairs on which the strategy is ran
        exchanges = exchanges on which the strategy is ran
        strategy_parameters = all strategy parameters
        """
        super(PairTrading, self).__init__(pairs, exchanges, strategy_parameters)
        self.exchange = exchanges[0]
        self.ccy1 = self.pairs[0]
        self.ccy2 = self.pairs[1]

        if len(self.pairs) != 2:
            self.log.error('Pair Trading only doable on two assets at the moment')
            raise ValueError('Only use two assets.')

    def get_data_for_backtest(self, data_location):
        data_ccy1 = utilities.get_data_from_local(data_location, self.ccy1)
        data_ccy2 = utilities.get_data_from_local(data_location, self.ccy2)

        data_ccy1 = data_ccy1.add_suffix('_' + self.ccy1)
        data_ccy2 = data_ccy2.add_suffix('_' + self.ccy2)
        data_ccy1 = data_ccy1[:-1]
        data_ccy2 = data_ccy2[:-1]

        data_ccy1['close_return_' + self.ccy1] = data_ccy1['close_' + self.ccy1].pct_change().fillna(0)
        data_ccy2['close_return_' + self.ccy2] = data_ccy2['close_' + self.ccy2].pct_change().fillna(0)

        data = pd.concat([data_ccy1, data_ccy2], axis=1).dropna()
        return data

    def clean_and_extend_data(self, data):
        return data

    def compute_stats(self, data, strategy_parameters, iteration):
        if iteration > 0:
            return {
                'avg_error': np.average(data.errors.dropna()),
                'std_error': np.std(data.errors.dropna())
            }
        else:
            return {
                'avg_error': 0,
                'std_error': 1
            }

    def compute_signal(self, data, stats_past, strategy_parameters, iteration):
        """
        data = ohlc of the pairs
        stats_past = statistics on past data
        strategy_parameters = parameters of strategy
        iteration = iteration at which we are
        """

        if strategy_parameters['model'] == 'Ridge':
            X = data[['close_' + self.ccy1]]
            Y = data[['close_' + self.ccy2]]
            fit_intercept = False
            model = Ridge(alpha=0.0, fit_intercept=fit_intercept)
            model.fit(X, Y)
            yfit = model.predict(X)
            errors = Y - yfit

            if fit_intercept:
                intercept = model.intercept_[0]
            else:
                intercept = 0

            return {
                'intercept': intercept,
                'beta': model.coef_[0][0],
                'ypredict': yfit[-1][0],
                'y': Y.values[-1][0],
                'errors': errors.values[-1][0],
                'r2': model.score(X, Y)
            }
        elif strategy_parameters['model'] == 'Kalman':
            X = data['close_' + self.ccy1]
            Y = data['close_' + self.ccy2]
            delta = 1e-5
            trans_cov = delta / (1 - delta) * np.eye(1)
            obs_mat = np.vstack([X]).T[:, np.newaxis]

            kf = KalmanFilter(
                n_dim_obs=1,
                n_dim_state=1,
                initial_state_mean=(Y[0]/X[0]),
                initial_state_covariance=np.ones((1, 1)),
                transition_matrices=np.eye(1),
                observation_matrices=obs_mat,
                observation_covariance=np.eye(1),
                transition_covariance=trans_cov,
            )
            state_means, state_covs = kf.filter(Y.values)

            ypredict = X * state_means[:, 0]
            y = Y.values

            return {
                'intercept': 0,
                'beta': state_means[-1][0],
                'ypredict': ypredict[-1],
                'y': y[-1],
                'errors': y[-1] - ypredict[-1],
                'r2': r2_score(y, ypredict)
            }
        else:
            raise RuntimeError('Model unknown for pair trading')


    def compute_pnl(self, data, stats_signal, stats_past, strategy_parameters, iteration):
        """
        data = ohlc of the pairs
        stats_signal = signal and associated values
        stats_past = stats on historical data passed in
        strategy_parameters = parameters of strategy
        """
        series1 = 'close_' + self.ccy1
        series2 = 'close_' + self.ccy2
        log_return1 = math.log(data[series1].tail(1).values[0]/data[series1].head(1).values[0])
        log_return2 = math.log(data[series2].tail(1).values[0]/data[series2].head(1).values[0])

        signal = (stats_signal['errors'] - stats_past['avg_error']) / stats_past['std_error']

        if iteration<5 or (stats_signal['r2'] < 0):
            trade = 0
            pnl = 0
        else:
            if signal < -strategy_parameters['z_score_target']:
                trade = 1
                pnl = log_return2 - log_return1
            elif signal > strategy_parameters['z_score_target']:
                trade = 1
                pnl = log_return1 - log_return2
            else:
                trade = 0
                pnl = 0

        return {
            'pnl': pnl,
            'trade': trade,
            'signal': signal,
        }

    def print_backtest_stats(self, data):
        fig = plt.figure()

        series1 = 'close_' + self.ccy1
        series2 = 'close_' + self.ccy2

        ax1 = fig.add_subplot(311)
        ax2 = ax1.twinx()
        ax1.plot(pd.to_datetime(data.index), data[series1], 'g-', label=series1)
        ax2.plot(pd.to_datetime(data.index), data[series2], 'b-', label=series2)
        ax1.set_ylabel(series1, color='g')
        ax2.set_ylabel(series2, color='b')
        ax1.grid(True)

        ax3 = fig.add_subplot(312)
        number_of_dates = len(data[series1])
        colour_map = plt.cm.get_cmap('YlOrRd')
        colours = np.linspace(0.1, 1, number_of_dates)
        scatterplot = ax3.scatter(data[series1], data[series2], s=30, c=colours, cmap=colour_map, edgecolor='k', alpha=0.8)
        colourbar = plt.colorbar(scatterplot)
        colourbar.ax.set_yticklabels([str(p.date()) for p in data[::number_of_dates//9].index])
        ax3.set_xlabel(series1)
        ax3.set_ylabel(series2)
        ax3.grid(True)

        ax4 = fig.add_subplot(313)
        ax4.plot(pd.to_datetime(data.index), data.errors, 'r-')
        ax4.set_xlabel('time')
        ax4.set_ylabel('errors', color='r')
        ax4.grid(True)

        plt.show()

        fig = plt.figure()
        ax5 = fig.add_subplot(311)
        data['cumpnl'] = np.cumprod(1 + data['pnl'])
        ax6 = ax5.twinx()
        ax5.plot(pd.to_datetime(data.index), data.signal, 'g-')
        ax6.plot(pd.to_datetime(data.index), data.cumpnl, 'b-')
        ax5.set_ylabel('signal', color='g')
        ax5.set_ylim([-5, 5])
        ax5.plot(pd.to_datetime(data.index), data.signal * 0 + self.strategy_parameters['z_score_target'], 'g--')
        ax5.plot(pd.to_datetime(data.index), data.signal * 0 - self.strategy_parameters['z_score_target'], 'g--')
        ax6.set_ylabel('pnl', color='b')

        ax7 = fig.add_subplot(312)
        ax8 = ax7.twinx()
        ax7.plot(pd.to_datetime(data.index), data.r2, 'b-')
        data['cum_trades'] = np.cumsum(data['trade'])
        ax8.plot(pd.to_datetime(data.index), data.cum_trades, 'r-')
        ax7.set_ylabel('r2', color='b')
        ax8.set_ylabel('cum_trades', color='r')

        ax9 = fig.add_subplot(313)
        ax10 = ax9.twinx()
        ax9.plot(pd.to_datetime(data.index), data.beta, 'g-')
        ax10.plot(pd.to_datetime(data.index), data.intercept, 'b-')
        ax9.set_ylabel('beta', color='g')
        ax10.set_ylabel('intercept', color='b')

        plt.show()

        self.adf_test(data['errors'])

    def adf_test(self, series):
        result = adfuller(series)
        print('ADF Statistic: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))
