import abc


class OrderInterface:
    __metaclass__ = abc.ABCMeta

    def __init__(self, order_attributes):
        """
        order_attributes contains:

        price = price at which order is created
        price2 = secondary price needed for some orders
        quantity = quantity of shares to execute
        buysell = if you want to buy or sell
        order_type = market, limit, stop, etc
        leverage = amount of leverage desired
        pair = currency pair on which to trade
        time_start = scheduled start time
        time_end = expiration time of the order
        orderID = internal ID
        userref = user reference id
        validate = validate inputs only. Do not submit order
        """
        self.price = order_attributes.price
        self.price2 = order_attributes.price2
        self.quantity = order_attributes.quantity
        self.buysell = order_attributes.buysell
        self.order_type = order_attributes.order_type
        self.leverage = order_attributes.leverage
        self.pair = order_attributes.pair
        self.flags = order_attributes.flags
        self.time_start = order_attributes.time_start
        self.time_end = order_attributes.time_end
        self.id = order_attributes.orderID
        self.validate = order_attributes.validate
        self.userref = order_attributes.userref
