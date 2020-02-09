import argparse

from core.bots import DataBot
from core.logger import get_logger
from core.strategies import CollectData
from core.exchanges import Kraken

# TBD: remove ref in config.py in core - to discuss with Fiodor
PAIRS = [
    'XETHZEUR',
    'XETHZUSD',
    'XXBTZUSD',
    ]
EXCHANGES = {
    'kraken': Kraken()
    }


log = get_logger('collector')

def create_exchange(name):
    ''' Create exchange interface from exchange id
    :param name: exchange id
    :param type: str
    :result: ExchangeInterface instance
    '''
    if name in EXCHANGES:
        # create exchange
        return EXCHANGES[name]
    raise ValueError('unknown exchange `%s`' % name)


def collect(path, pairs, exchange, frequency, bot):
    ''' Collect data and persist to path
    :param path: location to persist data
    :param pairs: list of tickers
    :param exchange: exchange interface
    :param frequency: data frequency in minutes
    :param bot: run as bot
    '''

    parameters = {
        'filepath': path,
        'filenames': pairs,
        'data_frequency': frequency,
        }

    log.info('Collecting Data ...')
    log.info('\tpairs=%s' % pairs)
    log.info('\texchange=%s' % exchange)
    log.info('\tparameters=%s' % parameters)
        
    strategy = CollectData(pairs, [exchange], parameters)
    
    if bot:
        databot = DataBot(None, strategy)
        databot.run(cycle_time=3600)
    else:
        data = strategy.get_data()
        strategy.save_data(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default='' ,
                        help='location for the data')
    parser.add_argument('--pairs', nargs='*', 
                        default=PAIRS, choices=PAIRS,
                        help='tickers id')
    parser.add_argument('--exchange', type=create_exchange,
                        default='kraken', choices=EXCHANGES.keys(), 
                        help='exchange id (default: kraken)')
    parser.add_argument('--frequency', type=int, default=1, 
                        help='data frequency in minutes (default: 1)')
    parser.add_argument('--bot', action='store_true', 
                        help='if True, run bot, otherwise one shot data dump')
    
    args = parser.parse_args()
    collect(**vars(args))
