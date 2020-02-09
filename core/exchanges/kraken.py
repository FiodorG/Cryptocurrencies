from .exchange import ExchangeInterface
import datetime
import pytz
import krakenex
import pandas as pd
import numpy as np


class Kraken(ExchangeInterface):

    def __init__(self):
        """
        """
        api = krakenex.API()
        taker_fee = 0.0026
        maker_fee = 0.0016
        super(Kraken, self).__init__(api, taker_fee, maker_fee)

    def __replace_nixtime_by_datetime(self, query, index):
        """
        query = list of lists containing a nixtime at the index
        index = see above
        """
        query_with_datetime = list()
        for snap in query:
            snap[index] = str(datetime.datetime.fromtimestamp(snap[index], tz=pytz.utc))
            query_with_datetime.append(snap)
        return query_with_datetime

    def __check_query_valid(self, query):
        if 'result' not in query:
            raise Warning('Exchange query empty')

    def get_ohlc(self, pair, interval, since):
        """
        pair = asset pair to get OHLC data for
        interval = time frame interval in minutes (optional):
        1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600
        since = return committed OHLC data since given id (optional. exclusive)
        """
        query = self.api.query_public('OHLC', req={'pair': pair, 'interval': interval, 'since': str(since)})
        self.__check_query_valid(query)

        ohlc = query['result'][pair]
        self.last_query_time[pair] = query['result']['last'] # last = id to be used as since when polling for new, committed OHLC data
        query_with_datetime = self.__replace_nixtime_by_datetime(ohlc, 0)

        headers = ['datetime', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(query_with_datetime, columns=headers)
        df.set_index(['datetime'], inplace=True)
        df = df.astype(float)
        return df

    def get_order_book(self, pairs, count):
        """
        pairs = asset pairs to get market depth for
        count = maximum number of asks/bids (optional)
        Returns:
        asks = ask side array of array entries(<price>, <volume>, <timestamp>)
        bids = bid side array of array entries(<price>, <volume>, <timestamp>)
        """
        data = {}
        for pair in pairs:
            query = self.api.query_public('Depth', req={'pair': pair, 'count': count})
            self.__check_query_valid(query)

            bid = query['result'][pair]['bids']
            ask = query['result'][pair]['asks']

            bid_with_datetime = self.__replace_nixtime_by_datetime(bid, 2)
            ask_with_datetime = self.__replace_nixtime_by_datetime(ask, 2)

            headers = ['price', 'quantity', 'datetime']
            df_bid = pd.DataFrame(bid_with_datetime, columns=headers)
            df_bid.set_index(['datetime'], inplace=True)
            df_bid = df_bid.astype(float)
            df_bid['depth_quote'] = np.cumsum(df_bid['price'] * df_bid['quantity'])
            df_bid['depth_base'] = np.cumsum(df_bid['quantity'])
            df_bid['vwap'] = df_bid['depth_quote'] / np.cumsum(df_bid['quantity'])

            df_ask = pd.DataFrame(ask_with_datetime, columns=headers)
            df_ask.set_index(['datetime'], inplace=True)
            df_ask = df_ask.astype(float)
            df_ask['depth_quote'] = np.cumsum(df_ask['price'] * df_ask['quantity'])
            df_ask['depth_base'] = np.cumsum(df_ask['quantity'])
            df_ask['vwap'] = df_ask['depth_quote'] / np.cumsum(df_ask['quantity'])

            data[pair] = {'bid': df_bid, 'ask': df_ask}

        return data

    def get_ticker_data(self, pair):
        """
        pair = currency pair to get data from
        Returns:
        a = ask array(<price>, <whole lot volume>, <lot volume>),
        b = bid array(<price>, <whole lot volume>, <lot volume>),
        c = last trade closed array(<price>, <lot volume>),
        v = volume array(<today>, <last 24 hours>),
        p = volume weighted average price array(<today>, <last 24 hours>),
        t = number of trades array(<today>, <last 24 hours>),
        l = low array(<today>, <last 24 hours>),
        h = high array(<today>, <last 24 hours>),
        o = today's opening price
        """
        query = self.api.query_public('Ticker', req={'pair': pair})
        self.__check_query_valid(query)

        query = query['result'][pair]
        return query

    def get_trades_data(self, pair, since):
        """
        pair = asset pair to get trade data for
        since = return trade data since given id (optional. exclusive)
        Returns:
        array of array entries(<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>)
        last = id to be used as since when polling for new trade data
        """
        query = self.api.query_public('Trades', req={'pair': pair, 'since': str(since)})
        self.__check_query_valid(query)

        query = query['result'][pair]
        query_with_datetime = self.__replace_nixtime_by_datetime(query, 2)

        headers = ['price', 'quantity', 'datetime', 'buysell', 'order', 'x']
        df = pd.DataFrame(query_with_datetime, columns=headers)
        df.set_index(['datetime'], inplace=True)
        return df

    def place_order(self, order):
        """
        order = order to be executed
        pair = asset pair
        =======================================================================
        From the API:
        type = type of order (buy/sell)
        ordertype = order type:
            market
            limit (price = limit price)
            stop-loss (price = stop loss price)
            take-profit (price = take profit price)
            stop-loss-profit (price = stop loss price, price2 = take profit price)
            stop-loss-profit-limit (price = stop loss price, price2 = take profit price)
            stop-loss-limit (price = stop loss trigger price, price2 = triggered limit price)
            take-profit-limit (price = take profit trigger price, price2 = triggered limit price)
            trailing-stop (price = trailing stop offset)
            trailing-stop-limit (price = trailing stop offset, price2 = triggered limit offset)
            stop-loss-and-limit (price = stop loss price, price2 = limit price)
            settle-position
        price = price (optional.  dependent upon ordertype)
        price2 = secondary price (optional.  dependent upon ordertype)
        volume = order volume in lots
        leverage = amount of leverage desired (optional.  default = none)
        oflags = comma delimited list of order flags (optional):
            viqc = volume in quote currency (not available for leveraged orders)
            fcib = prefer fee in base currency
            fciq = prefer fee in quote currency
            nompp = no market price protection
            post = post only order (available when ordertype = limit)
        starttm = scheduled start time (optional):
            0 = now (default)
            +<n> = schedule start time <n> seconds from now
            <n> = unix timestamp of start time
        expiretm = expiration time (optional):
            0 = no expiration (default)
            +<n> = expire <n> seconds from now
            <n> = unix timestamp of expiration time
        userref = user reference id.  32-bit signed number.  (optional)
        validate = validate inputs only.  do not submit order (optional)
        """
        k = self.api
        k.load_key('kraken.key')

        result = k.query_private(
            'AddOrder',
            {
                'pair':      order.pair,
                'type':      order.buysell,
                'ordertype': order.order_type,
                'price':     order.price,
                'price2':    order.price2,
                'volume':    order.quantity,
                'leverage':  order.leverage,
                'oflags':    order.flags,
                'starttm':   order.time_start,
                'expiretm':  order.time_end,
                'userref':   order.userref,
                'validate':  order.validate,
            }
        )
        return result
