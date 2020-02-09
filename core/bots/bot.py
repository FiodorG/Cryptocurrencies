import abc
import time
import datetime
from ..logger import Logger


class BotInterface:
    __metaclass__ = abc.ABCMeta

    def __init__(self, config, strategy, test_mode):
        """
        config = config containing general information
        strategy = handle to object describing the strategy
        test_mode = blank run the algorithm
        """
        self.config = config
        self.strategy = strategy

        self.error = False
        self.log = Logger()

        self.time_start = -1
        self.time_last_cycle = -1
        self.warning_sleep_time = 300

        self.test_mode = test_mode

    def utc_time(self):
        return datetime.datetime.utcnow()

    def run(self, cycle_time=0):
        """
        cycle_time = time in seconds for a cycle duration
        """
        self.time_start = self.utc_time()
        self.time_last_cycle = self.time_start
        cycle_time = datetime.timedelta(seconds=cycle_time)

        self.log.info('Run starting')

        while not self.error:
            try:
                self.cycle()

                delta = self.utc_time() - self.time_last_cycle
                if (delta < cycle_time):
                    sleep_time = cycle_time - delta
                    self.log.info('Sleeping for %s' % str(sleep_time))
                    time.sleep(sleep_time.total_seconds())

                self.time_last_cycle = self.utc_time()

            except Warning as warning:
                self.log.warning('Warning: %s' % str(warning))
                self.log.warning('Warning: sleeping for %s' % str(self.warning_sleep_time))
                time.sleep(self.warning_sleep_time)

            except Exception as exception:
                self.log.error('Error: %s' % str(exception))
                self.log.error('Error: Execution interrupted')
                self.error = True
