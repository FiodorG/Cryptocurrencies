from .strategy import StrategyInterface
from ..utilities import utilities


class CollectData(StrategyInterface):

    def __init__(self, pairs, exchanges, strategy_parameters):
        """
        pairs = currency pairs on which the strategy is ran
        exchanges = exchanges on which the strategy is ran
        strategy_parameters = all strategy parameters
        including:
            filepath = where to save the data
            filename = name of the file
        """
        super(CollectData, self).__init__(pairs, exchanges, strategy_parameters)
        self.exchange = exchanges[0]
        self.filepath = strategy_parameters['filepath']
        self.filenames = strategy_parameters['filenames']
        self.data_frequency = strategy_parameters['data_frequency']

        if len(exchanges) != 1:
            raise ValueError('Can only do one exchange now.')

        self.exchange.set_last_query_time_from_pairs(pairs)

    def get_data(self):
        exchange = self.exchanges[0]
        ohlc = {pair: exchange.get_ohlc(pair, self.data_frequency, since=exchange.last_query_time) for pair in self.pairs}
        return ohlc

    def save_data(self, data):
        for pair, filename in zip(self.pairs, self.filenames):
            utilities.save_data_to_local(data[pair], self.filepath, filename)
            self.log.ok('Data for %s saved to %s\%s' % (pair, self.filepath, filename))