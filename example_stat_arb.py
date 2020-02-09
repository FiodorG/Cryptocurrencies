#from core.bots import DataBot
#from core.strategies import CollectData
#from core.exchanges import Kraken
#import config as config
#
#import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
#from statsmodels.tsa.stattools import adfuller
#from sklearn.linear_model import Ridge


#def plot_time_series(data, series1, series2):
#    fig = plt.figure()
#
#    ax1 = fig.add_subplot(311)
#    ax2 = ax1.twinx()
#    ax1.plot(pd.to_datetime(data.index), data[series1], 'g-', label=series1)
#    ax2.plot(pd.to_datetime(data.index), data[series2], 'b-', label=series2)
#    ax1.set_ylabel(series1, color='g')
#    ax2.set_ylabel(series2, color='b')
#    ax1.grid(True)
#
#    ax3 = fig.add_subplot(312)
#    ax3.plot(data[series1], data[series2], 'o')
#    ax3.set_xlabel(series1)
#    ax3.set_ylabel(series2)
#    ax3.grid(True)
#
#    ax4 = fig.add_subplot(313)
#    ax4.plot(pd.to_datetime(data.index), data.errors, 'r-')
#    ax4.set_xlabel('time')
#    ax4.set_ylabel('errors', color='r')
#    ax4.grid(True)
#
#    plt.show()
#
#    fig = plt.figure()
#    ax5 = fig.add_subplot(311)
#    data['cumpnl'] = np.cumsum(data['pnl'])
#    ax6 = ax5.twinx()
#    ax5.plot(pd.to_datetime(data.index), data.signal, 'g-')
#    ax6.plot(pd.to_datetime(data.index), data.cumpnl, 'b-')
#    ax5.set_ylabel('signal', color='g')
#    ax6.set_ylabel('pnl', color='b')
#
#    ax7 = fig.add_subplot(312)
#    ax8 = ax7.twinx()
#    ax7.plot(pd.to_datetime(data.index), data.r2, 'b-')
#    data['cum_trades'] = np.cumsum(data['trade'])
#    ax8.plot(pd.to_datetime(data.index), data.cum_trades, 'r-')
#    ax7.set_ylabel('r2', color='b')
#    ax8.set_ylabel('cum_trades', color='r')
#
#    ax9 = fig.add_subplot(313)
#    ax10 = ax9.twinx()
#    ax9.plot(pd.to_datetime(data.index), data.beta, 'g-')
#    ax10.plot(pd.to_datetime(data.index), data.intercept, 'b-')
#    ax9.set_ylabel('beta', color='g')
#    ax10.set_ylabel('intercept', color='b')
#
#    plt.show()

#def adf_test(series):
#    result = adfuller(series)
#    print('ADF Statistic: %f' % result[0])
#    print('p-value: %f' % result[1])
#    print('Critical Values:')
#    for key, value in result[4].items():
#    	print('\t%s: %.3f' % (key, value))


#def compute_signal(data_past, stats_past, strategy_parameters):
#    X = data_past[['close_' + strategy_parameters['ccys'][0]]]
#    Y = data_past[['close_' + strategy_parameters['ccys'][1]]]
#    fit_intercept = False
#    model = Ridge(alpha=0.0, fit_intercept=fit_intercept)
#    model.fit(X, Y)
#    yfit = model.predict(X)
#    errors = Y - yfit
#
#    if fit_intercept:
#        intercept = model.intercept_[0]
#    else:
#        intercept = 0
#
#    return {
#        'alpha': model.alpha,
#        'intercept': intercept,
#        'beta': model.coef_[0][0],
#        'ypredict': yfit[-1][0],
#        'y': Y.values[-1][0],
#        'errors': errors.values[-1][0],
#        'r2': model.score(X, Y)
#    }


#def compute_pnl(data_future, stats_signal, stats_past, strategy_parameters):
#    series = 'close_' + strategy_parameters['ccys'][1]
#    log_return = data_future[series].tail(1).values[0]/data_future[series].head(1).values[0] - 1
#
#    signal = (stats_signal['errors'] - stats_past['avg_error']) / stats_past['std_error']
#    if signal < -strategy_parameters['z_score_target']:
#        trade = 1
#        pnl = log_return
#    elif signal > strategy_parameters['z_score_target']:
#        trade = 1
#        pnl = -log_return
#    else:
#        trade = 0
#        pnl = 0
#
#    return {
#        'pnl': pnl,
#        'trade': trade,
#        'signal': signal,
#    }


#def compute_stats(data, strategy_parameters):
#
#    if 'errors' in data.columns:
#        return {
#            'avg_error': np.average(data.errors.dropna()),
#            'std_error': np.std(data.errors.dropna())
#        }
#    else:
#        return {
#            'avg_error': 0,
#            'std_error': 1
#        }


#def backtest(data, frequency, window, strategy_parameters):
#    result = data.copy()
#
#    for i in range(window - 1, len(data.index), frequency):
#
#        if len(data) - i >= frequency:
#            data_past = data.iloc[i - window + 1:i + 1, :].copy()
#            data_future = data.iloc[i:i + frequency + 1, :].copy()
#            index = data_past.index[-1]
#
#            stats_past = compute_stats(result, strategy_parameters)
#            stats_signal = compute_signal(data_past, stats_past, strategy_parameters)
#            stats_pnl = compute_pnl(data_future, stats_signal, stats_past, strategy_parameters)
#
#            for key, value in stats_past.items():
#                result.set_value(index, key, value)
#
#            for key, value in stats_signal.items():
#                result.set_value(index, key, value)
#
#            for key, value in stats_pnl.items():
#                result.set_value(index, key, value)
#
#    result = result.dropna()
#    return result

#ccy1 = 'XETHZUSD' # 'XETHZUSD'
#ccy2 = 'XLTCZUSD' # 'XXBTZUSD'
#
#pairs = [ccy1, ccy2]
#exchanges = [Kraken()]
#strategy_parameters = {
#    'ccys': [ccy1, ccy2],
#    'filepath': 'C:\\Users\\gorokf\\Dropbox\\Kraken\\',
#    'filenames': [ccy1, ccy2],
#    'data_frequency': 5,  # minutes
#    'z_score_target': 2,
#}

strategy = CollectData(pairs, exchanges, strategy_parameters)
bot = DataBot(config, strategy, 1)
data_raw = bot.strategy.get_data()

data_ccy1 = data_raw[ccy1]
data_ccy2 = data_raw[ccy2]
data_ccy1 = data_ccy1.add_suffix('_' + ccy1)
data_ccy2 = data_ccy2.add_suffix('_' + ccy2)
data_ccy1 = data_ccy1[:-1]
data_ccy2 = data_ccy2[:-1]

data_ccy1['close_return_' + ccy1] = data_ccy1['close_' + ccy1].pct_change().fillna(0)
data_ccy2['close_return_' + ccy2] = data_ccy2['close_' + ccy2].pct_change().fillna(0)

data = pd.concat([data_ccy1, data_ccy2], axis=1).dropna()

#adf_test(data['close_return_' + ccy1])
#adf_test(data['close_return_' + ccy2])

result = backtest(data, frequency=1, window=120, strategy_parameters=strategy_parameters)
plot_time_series(result, 'close_' + ccy1, 'close_' + ccy2)

#adf_test(result['errors'])
