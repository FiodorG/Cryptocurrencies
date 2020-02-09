from core.bots import BacktestBot
from core.strategies import PairTrading
from core.exchanges import Kraken
import config as config

ccy1 = 'XETHZUSD' # 'XETHZUSD' 'XETHZUSD'
ccy2 = 'XLTCZUSD' # 'XXBTZUSD' 'XLTCZUSD'

pairs = [ccy1, ccy2]
exchanges = [Kraken(), Kraken()]
data_location = 'C:\\Users\\gorokf\\Dropbox\\Kraken\\'
strategy_parameters = {
    'ccys': [ccy1, ccy2],
    'filepath': 'C:\\Users\\gorokf\\Dropbox\\Kraken\\',
    'filenames': [ccy1, ccy2],
    'data_frequency': 5,  # minutes
    'z_score_target': 2,
    'frequency': 1,
    'window': 120,
    'model': 'Kalman',
}

strategy = PairTrading(pairs, exchanges, strategy_parameters)
bot = BacktestBot(config, strategy, data_location)
backtest_result = bot.run()