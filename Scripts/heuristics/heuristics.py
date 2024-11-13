import abc
from collections import defaultdict


class Heuristics:
    def __init__(self):
        self.scores = defaultdict(int)

    @abc.abstractmethod
    def initialize_scores(self, clauses):
        pass

    @abc.abstractmethod
    def conflict(self, conflict_clause):
        pass

    @abc.abstractmethod
    def decay_scores(self):
        pass

    def decide(self, assigned_literals):
        pass
