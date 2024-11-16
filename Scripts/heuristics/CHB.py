from collections import defaultdict

from Scripts.heuristics.heuristics import Heuristics


class CHBHeuristics(Heuristics):
    def __init__(self, initial_alpha=0.4, decay_rate=1e-6, min_alpha=0.06):
        super().__init__()
        self.alpha = initial_alpha
        self.min_alpha = min_alpha
        self.decay_rate = decay_rate
        self.conflict_count = 0
        self.last_conflict = defaultdict(int)

    def initialize_scores(self, clauses):
        """Initialize Q and last_conflict for all variables involved in clauses."""
        for clause in clauses:
            for literal in clause:
                # Initialize to default value (0) if not already present
                self.scores[literal]
                self.last_conflict[literal]

    def conflict(self, conflict_clause):
        """Handle the conflict by updating Q scores and tracking the conflict."""
        self.conflict_count += 1
        for literal in conflict_clause:
            reward = self._calculate_reward(literal)
            self.scores[literal] = (1 - self.alpha) * self.scores[literal] + self.alpha * reward
            self.last_conflict[literal] = self.conflict_count
        self._decay_alpha()

    def decay_scores(self):
        """Decay all scores by multiplying with the current alpha."""
        for literal in self.scores:
            self.scores[literal] *= self.alpha

    def update_scores(self, variable, reward):
        """Update the score for a given variable based on the reward."""
        self.scores[variable] = (1 - self.alpha) * self.scores[variable] + self.alpha * reward

    def decide(self, assigned_literals):
        """Decide on the next variable to assign based on the current scores."""
        # Exclude already assigned variables
        unassigned = set(self.scores.keys()) - set(assigned_literals) - set(-literal for literal in assigned_literals)
        best_var = max(unassigned, key=lambda x: self.scores[x], default=None)
        # Print the value of best_var and its type
        if best_var is None:
            return None  # If no variable is available, return None instead of "SAT"
        return int(best_var)  # Ensure the returned value is an integer

    # CHB specific
    def _calculate_reward(self, literal):
        """Calculate reward for a literal based on the conflict count."""
        return 1 / (self.conflict_count - self.last_conflict[literal] + 1)

    def _decay_alpha(self):
        """Decay alpha based on the conflict count."""
        if self.alpha > self.min_alpha:
            self.alpha = max(self.min_alpha, self.alpha - self.decay_rate)
