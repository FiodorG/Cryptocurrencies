from abc import ABCMeta, abstractmethod


class ExchangeInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_ohlc(self): raise NotImplementedError

    @abstractmethod
    def get_order_book(self): raise NotImplementedError

    @abstractmethod
    def get_ticker_data(self): raise NotImplementedError

    @abstractmethod
    def get_trades_data(self): raise NotImplementedError

    def __init__(self, api, taker_fee, maker_fee):
        """
        api = exchange api
        taker_fee = fee to cross bid-ask
        maker_fee = fee to make markets
        """
        self.api = api
        self.last_query_time = {}  # time of last query per asset
        self.taker_fee = taker_fee
        self.maker_fee = maker_fee

    def set_last_query_time_from_pairs(self, pairs):
        """
        pairs = pairs which are going to be queried
        """
        self.last_query_time = {pair: 0 for pair in pairs}
