import random
from collections import defaultdict


class CDCL:
    def __init__(self, clauses):
        self.clauses = clauses
        self.assignment = {}  # Variable assignments
        self.decision_level = 0
        self.decision_stack = []  # Track decisions and propagations
        self.scores = defaultdict(int)  # VSIDS scores for each variable
        self.decay_factor = 0.95  # Decay factor for scores
        self.conflict_clause = None

    def increment_score(self, clause):
        """Increases the scores of variables in the latest conflict clause."""
        for literal in clause:
            var = abs(literal)
            self.scores[var] += 1

    def decay_scores(self):
        """Decays the scores periodically."""
        for var in self.scores:
            self.scores[var] *= self.decay_factor

    def select_variable(self):
        """Selects the next variable to assign, using the highest VSIDS score."""
        unassigned_vars = [v for v in self.scores if v not in self.assignment]
        if not unassigned_vars:
            return None
        # Choose the variable with the highest VSIDS score
        return max(unassigned_vars, key=lambda var: self.scores[var])

    def unit_propagate(self):
        """Performs unit propagation and returns a conflict clause if a conflict occurs."""
        while True:
            unit_clause = None
            for clause in self.clauses:
                unassigned = [l for l in clause if abs(l) not in self.assignment]
                # Check if all literals are assigned but clause is unsatisfied (conflict)
                if not unassigned and not any(self.assignment.get(abs(l)) == (l > 0) for l in clause):
                    self.conflict_clause = clause  # Conflict found
                    return clause
                # Check for a unit clause (one unassigned literal and others false)
                elif len(unassigned) == 1:
                    unit_clause = unassigned[0]
                    break
            if not unit_clause:
                return None  # No more unit clauses to propagate
            self.assign(unit_clause, clause=clause)
            if self.conflict_clause:
                return self.conflict_clause  # Return conflict clause

    def assign(self, literal, clause):
        """Assigns a value to a variable and logs the decision level."""
        var = abs(literal)
        value = literal > 0
        if var in self.assignment:
            if self.assignment[var] != value:
                self.conflict_clause = clause  # Conflict detected
            return
        self.assignment[var] = value
        self.decision_stack.append((var, self.decision_level))

    def backtrack(self, level):
        """Backtracks to a previous decision level."""
        while self.decision_stack and self.decision_stack[-1][1] > level:
            var, _ = self.decision_stack.pop()
            del self.assignment[var]
        self.decision_level = level

    def solve(self):
        """Main solving function using VSIDS."""
        while True:
            # Perform unit propagation; if conflicts, analyze conflict
            conflict_clause = self.unit_propagate()
            if conflict_clause is not None:
                self.increment_score(conflict_clause)  # Update VSIDS scores
                self.decay_scores()  # Decay scores periodically
                backtrack_level = max(0, self.decision_level - 1)
                self.backtrack(backtrack_level)
                if backtrack_level == 0:
                    return "Unsatisfiable"
            else:
                # Select the next decision variable using VSIDS
                var = self.select_variable()
                if var is None:
                    return "Satisfiable"  # No unassigned variables left, solution found
                # Make a decision and increase decision level
                self.decision_level += 1
                decision = random.choice([True, False])
                self.assign(var if decision else -var, None)

    def get_solution(self):
        """Returns the current assignment as the solution."""
        return self.assignment


# Example usage with a sample set of clauses
clauses = [[1], [-1]]

solver = CDCL(clauses)
result = solver.solve()
print("Result:", result)
