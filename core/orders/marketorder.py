from .order import OrderInterface


class MarketOrder(OrderInterface):
    def __init__(self, order_attributes):
        """
        order_attributes contains:

        quantity = quantity of shares to execute
        buysell = if you want to buy or sell
        leverage = amount of leverage desired
        pair = currency pair on which to trade
        time_start = scheduled start time
        time_end = expiration time of the order
        orderID = internal ID
        userref = user reference id
        validate = validate inputs only. Do not submit order
        """

        order_attributes['price'] = 0
        order_attributes['price2'] = 0
        order_attributes['order_type'] = 'market'
        order_attributes['flags'] = []

        super(MarketOrder, self).__init__(order_attributes)
