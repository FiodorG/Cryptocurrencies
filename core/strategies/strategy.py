from abc import ABCMeta, abstractmethod
import numpy as np
import matplotlib.pyplot as plt
from ..utilities import utilities
from ..logger import Logger


class StrategyInterface:
    __metaclass__ = ABCMeta

    def __init__(self, pairs, exchanges, strategy_parameters):
        """
        pairs = currency pairs on which the strategy is ran
        exchanges = exchanges on which the strategy is ran
        strategy_parameters = all strategy parameters
        """
        self.pairs = pairs
        self.exchanges = exchanges
        self.strategy_parameters = strategy_parameters
        self.log = Logger()

    @abstractmethod
    def get_data_live(self): raise NotImplementedError

    @abstractmethod
    def get_data_for_backtest(self): raise NotImplementedError

    @abstractmethod
    def clean_and_extend_data(self): raise NotImplementedError

    @abstractmethod
    def compute_signal(self): raise NotImplementedError

    @abstractmethod
    def print_signal(self): raise NotImplementedError

    @abstractmethod
    def compute_stats(self): raise NotImplementedError

    @abstractmethod
    def generate_orders(self): raise NotImplementedError
