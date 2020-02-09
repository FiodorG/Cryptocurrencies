import traceback
from .bot import BotInterface


class DataBot(BotInterface):

    def __init__(self, config, strategy):
        """
        config = config containing general information
        strategy = handle to object describing the strategy
        """
        super(DataBot, self).__init__(config, strategy, 0)

    def cycle(self):
        self.log.info('Start of cycle')

        try:
            self.log.info('Getting data')
            data = self.strategy.get_data()

            self.log.info('Saving data')
            self.strategy.save_data(data)
        except:
            exception = traceback.format_exc()
            print(exception)
            raise RuntimeError('Error')
        else:
            self.log.info('No Errors')

        self.log.info('End of cycle')
