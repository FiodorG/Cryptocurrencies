from core.bots import BacktestBot
from core.strategies import TrendFollowing
from core.exchanges import Kraken
import config as config

data_location = 'C:\\Users\\gorokf\\Dropbox\\Kraken\\'
pairs = ['XETHZEUR']
exchanges = [Kraken()]
strategy_parameters = {
    'window': 100,
    'frequency': 100,
    'crossover_value': 50
}

strategy = TrendFollowing(pairs, exchanges, strategy_parameters)
bot = BacktestBot(config, strategy, data_location)
backtest_result = bot.run()