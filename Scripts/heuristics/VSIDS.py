from Scripts.heuristics.heuristics import Heuristics


class VSIDSHeuristics(Heuristics):
    def __init__(self, decay_factor=0.95):
        super().__init__()
        self.decay_factor = decay_factor

    def initialize_scores(self, clauses):
        for clause in clauses:
            for literal in clause:
                self.scores[literal] += 1

    def conflict(self, conflict_clause):
        for literal in conflict_clause:
            self.scores[literal] += 1
        self.decay_scores()

    def decay_scores(self):
        for literal in self.scores:
            self.scores[literal] *= self.decay_factor

    def update_scores(self, variable, reward):
        # VSIDS-specific logic to update the scores based on reward
        self.scores[variable] += reward

    def decide(self, assigned_literals):
        max_score, best_var = 0, 0
        assigned_set = set(assigned_literals)
        for item, score in self.scores.items():
            if score > max_score and item not in assigned_set and -item not in assigned_set:
                max_score, best_var = score, item
        return best_var
