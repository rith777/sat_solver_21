from collections import defaultdict

from Scripts.heuristics.heuristics import Heuristics

class CHBHeuristics(Heuristics):
    def __init__(self, initial_alpha=0.4, decay_rate=1e-6, min_alpha=0.06):
        super().__init__()
        self.alpha = initial_alpha
        self.min_alpha = min_alpha
        self.decay_rate = decay_rate
        self.conflict_count = 0
        self.Q = defaultdict(lambda: 0)  # Q score for each variable
        self.last_conflict = defaultdict(lambda: 0)  # Last conflict for each variable

    def initialize_scores(self, clauses):
        for clause in clauses:
            for literal in clause:
                if literal not in self.Q:
                    self.Q[literal] = 0
                if literal not in self.last_conflict:
                    self.last_conflict[literal] = 0

    def conflict(self, conflict_clause):
        self.conflict_count += 1
        for literal in conflict_clause:
            reward = self.calculate_reward(literal)
            self.Q[literal] = (1 - self.alpha) * self.Q[literal] + self.alpha * reward
            self.last_conflict[literal] = self.conflict_count
        self.decay_alpha()

    def calculate_reward(self, literal):
        last_conflict = self.last_conflict[literal]
        reward = 1 / (self.conflict_count - last_conflict + 1)
        return reward

    def decay_alpha(self):
        if self.alpha > self.min_alpha:
            self.alpha = max(self.min_alpha, self.alpha - self.decay_rate)

    def update_scores(self, variable, reward):
        self.Q[variable] = (1 - self.alpha) * self.Q[variable] + self.alpha * reward

    def decay_scores(self):
        for literal in self.Q:
            self.Q[literal] *= self.alpha

    def decide(self, assigned_literals):
        max_score, best_var = -float('inf'), None
        assigned_set = set(assigned_literals)
        for literal, score in self.Q.items():
            if score > max_score and literal not in assigned_set and -literal not in assigned_set:
                max_score, best_var = score, literal

        if best_var is None:
            print("No unassigned variable available. Returning 'SAT'.")
            return "SAT"  # No more unassigned variables

        # Debugging output
        print(f"Decided variable: {best_var}, Type: {type(best_var)}")  # Add this print
        return int(best_var)  # Ensure the returned value is an integer

    def two_watch_propagate(self, literal_watch, clauses_literal_watched, variable):
        print(f"Before conversion: variable={variable}, Type={type(variable)}")  # Debugging output

        # Ensure variable is an integer before negation
        variable = int(variable)  # Explicitly cast variable to int

        print(f"After conversion: variable={variable}, Type={type(variable)}")  # Debugging output

        try:
            # Check type of literal_watch[-variable] before usage
            print(f"Accessing literal_watch[-variable]: {literal_watch[-variable]}")
            for affected_claus_num in reversed(literal_watch[-variable]):
                # Your logic for propagating clauses here
                pass
        except Exception as e:
            print(f"Error accessing literal_watch[-variable]: {e}")
            raise

