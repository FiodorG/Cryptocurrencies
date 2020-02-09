from .strategy import StrategyInterface
from ..orders import MarketOrder


class TriangularArbitrage(StrategyInterface):

    def __init__(self, pairs, exchanges, strategy_parameters):
        """
        pairs = currency pairs on which the strategy is ran
        exchanges = exchanges on which the strategy is ran
        strategy_parameters = all strategy parameters
        including:
            bidask = whether the fx conversion will consume the bid or ask
            cash = initial sum of cash
            cash_currency = currency of initial cash
        """
        super(TriangularArbitrage, self).__init__(pairs, exchanges, strategy_parameters)
        self.bidask = strategy_parameters['bidask']
        self.cash = strategy_parameters['cash']
        self.cash_currency = strategy_parameters['cash_currency']
        self.exchange = exchanges[0]

        if len(self.exchanges) > 1:
            self.log.error('Triangular Arbitrage only doable on one exchange at the moment.')
            raise ValueError('Only use one exchange.')

        if len(self.pairs) + len(self.bidask) != 6:
            self.log.error('It takes 3 to make a triangle.')
            raise ValueError('Provide 3 pairs and 3 buysells.')

        # add check on cash currency

    def get_data_live(self):
        return self.exchange.get_order_book(self.pairs, count=100)

    def __convert_cash_bid(self, pair, data_for_pair, cash, fee):
        for idx, row in data_for_pair.iterrows():
            if row.depth_base >= cash:
                return cash * row.vwap * (1 - fee), fee * cash * row.vwap
        raise ValueError('Order book not deep enough for trade size.')

    def __convert_cash_ask(self, pair, data_for_pair, cash, fee):
        for idx, row in data_for_pair.iterrows():
            if row.depth_quote >= cash:
                return cash / row.vwap * (1 - fee), fee * cash
        raise ValueError('Order book not deep enough for trade size.')

    def __get_order_book_side_from_buysell(self, pair):
        bidask = self.bidask[pair]

        if bidask == 'buy':
            return 'ask'
        elif bidask == 'sell':
            return 'bid'
        else:
            raise ValueError('Buysell flag not recognized.')

    def compute_signal(self, data):
        """
        data = data containing the bids and asks of the pairs
        """
        initial_cash = self.cash
        cash = initial_cash
        steps = [initial_cash]
        fees = []

        for pair in self.pairs:
            bidask = self.__get_order_book_side_from_buysell(pair)

            if bidask == 'ask':
                cash, fee = self.__convert_cash_ask(pair, data[pair][bidask], cash, self.exchange.taker_fee)
            elif bidask == 'bid':
                cash, fee = self.__convert_cash_bid(pair, data[pair][bidask], cash, self.exchange.taker_fee)
            else:
                raise ValueError('Pairs should be either bid or ask.')

            steps.append(cash)
            fees.append(fee)

        return {
            'cash': steps,
            'fees': fees,
            'initial_cash': initial_cash,
            'final_cash': steps[-1],
            'currency': self.cash_currency,
            'pnl': steps[-1] - initial_cash
        }

    def print_signal(self, pnl):
        self.log.ok('Expected PNL: %.4f%s' % (pnl['pnl'], pnl['currency']))

    def generate_orders(self, data, signal):
        if signal['pnl'] < 0:
            return []
        else:
            orders = []
            for pair in self.pairs:
                order_attributes = {
                    'quantity': 0,
                    'buysell': self.bidask[pair],
                    'leverage': 1,
                    'pair': pair,
                    'time_start': 0,
                    'time_end': 10,
                    'orderID': 0,
                    'userref': 0,
                    'validate': 1,
                }
                orders.append(MarketOrder(order_attributes))
            return orders
