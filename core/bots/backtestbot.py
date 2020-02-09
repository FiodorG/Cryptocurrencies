import traceback
from .bot import BotInterface


class BacktestBot(BotInterface):

    def __init__(self, config, strategy, data_location):
        """
        config = config containing general information
        strategy = handle to object describing the strategy
        data_location = where the data for backtest is stored
        """
        super(BacktestBot, self).__init__(config, strategy, 0)
        self.data_location = data_location

    def run(self):
        time_start = self.utc_time()
        self.log.info('Backtest start')

        try:
            self.log.info('Getting data')
            data = self.strategy.get_data_for_backtest(self.data_location)
            data = self.strategy.clean_and_extend_data(data)

            self.log.info('Starting backtest')
            backtest_results = self.backtest(data)
            self.strategy.print_backtest_stats(backtest_results)
        except:
            exception = traceback.format_exc()
            print(exception)
            raise RuntimeError('Error')
        else:
            self.log.info('No Errors')

        self.log.info('Total time elapsed: %s' % (self.utc_time() - time_start))
        self.log.info('Backtest end')

        return backtest_results

    def backtest(self, data):
        result = data.copy()
        frequency = self.strategy.strategy_parameters['frequency']
        window = self.strategy.strategy_parameters['window']
        strategy_parameters = self.strategy.strategy_parameters

        iteration = 0
        for i in range(window - 1, len(data.index), frequency):

            if len(data) - i >= frequency:
                data_past = result.iloc[i - window + 1:i + 1, :].copy()
                data_future = result.iloc[i:i + frequency + 1, :].copy()
                index = data_future.index[-1]

                stats_past = self.strategy.compute_stats(data_past, strategy_parameters, iteration)
                stats_signal = self.strategy.compute_signal(data_past, stats_past, strategy_parameters, iteration)
                stats_pnl = self.strategy.compute_pnl(data_future, stats_signal, stats_past, strategy_parameters, iteration)

                for key, value in stats_past.items():
                    result.set_value(index, key, value)

                for key, value in stats_signal.items():
                    result.set_value(index, key, value)

                for key, value in stats_pnl.items():
                    result.set_value(index, key, value)

            iteration += 1

        result = result.dropna()
        return result
