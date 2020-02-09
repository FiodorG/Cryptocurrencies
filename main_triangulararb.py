from core.bots import TradingBot
from core.strategies import TriangularArbitrage
from core.exchanges import Kraken
import config as config

test_mode = 1
pairs = ['XETHZEUR', 'XETHXXBT', 'XXBTZEUR']
exchanges = [Kraken()]
strategy_parameters = {
    'cash': 100,
    'cash_currency': 'EUR',
    'bidask': {'XETHZEUR': 'buy', 'XETHXXBT': 'sell', 'XXBTZEUR': 'sell'}
}

strategy = TriangularArbitrage(pairs, exchanges, strategy_parameters)
bot = TradingBot(config, strategy, test_mode)

bot.run(cycle_time=10)
