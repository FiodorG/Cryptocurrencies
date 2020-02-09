from .bot import BotInterface


class TradingBot(BotInterface):

    def __init__(self, config, strategy, test_mode):
        """
        config = config containing general information
        strategy = handle to object describing the strategy
        test_mode = blank run the algorithm
        """
        super(TradingBot, self).__init__(config, strategy, test_mode)

    def cycle(self):
        self.log.info('Start of cycle')

        self.log.info('Getting data')
        data = self.strategy.get_data_live()
        data = self.strategy.clean_and_extend_data(data)

        self.log.info('Computing signal')
        signal = self.strategy.compute_signal(data)
        self.strategy.print_signal(signal)

        self.log.info('Generating orders')
        orders = self.strategy.generate_orders(data, signal)

        self.log.info('Sending orders')
        self.send_orders(orders)

        self.log.info('End of cycle')

    def send_orders(self, orders):
        if self.test_mode:
            self.log.ok('test order creation')
            # do something?
        else:
            self.log.ok('live order creation')
            # do something else
