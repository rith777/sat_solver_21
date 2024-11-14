from abc import ABC, abstractmethod
from collections import defaultdict


class Heuristics(ABC):
    def __init__(self):
        self.scores = defaultdict(int)
        self.last_conflict = defaultdict(int)

    @abstractmethod
    def initialize_scores(self, clauses):
        pass

    @abstractmethod
    def conflict(self, conflict_clause):
        pass

    @abstractmethod
    def decay_scores(self):
        pass

    @abstractmethod
    def update_scores(self, variable, reward):
        pass

    def decide(self, assigned_literals):
        pass
