import time
from collections import namedtuple
from enum import Enum, auto

from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_list_to_matrix, pretty_matrix
from Scripts.heuristics.VSIDS import VSIDSHeuristics
from Scripts.heuristics.CHB import CHBHeuristics

Pair = namedtuple('Pair', ['first', 'second'])


class SATResult(Enum):
    UNSATISFIABLE = auto()
    SATISFIABLE = auto()


class Status(Enum):
    SUCCESS = auto()
    CONFLICT = auto()
    FAILED = auto()


class ClauseStatus(Enum):
    SATISFIED = auto()
    UNSATISFIED = auto()
    UNRESOLVED = auto()
    UNIT = auto


class Statistics:
    def __init__(self):
        self.learned_counter = 0
        self.decision_counter = 0
        self.implications_counter = 0

    def increment_learned_counter(self):
        self.learned_counter += 1

    def increment_decision_counter(self):
        self.decision_counter += 1

    def increment_implicit_counter(self):
        self.implications_counter += 1

    def update_implications_counter(self, new_value):
        self.implications_counter = new_value

    def __str__(self):
        return f"""
        Learned clauses: {self.learned_counter}
        Amount of decisions: {self.decision_counter}
        Amount of implications: {self.implications_counter}
        """


class CDCLSatSolver:
    def __init__(self, clauses, total_variables, heuristics):
        self.clauses = clauses
        self.total_variables = total_variables
        self.assignment = []
        self.decision_levels = []

        self.heuristics = heuristics
        self.statistics = Statistics()

    def solve(self):

        self.unit_propagation()
        if self.clauses == Status.CONFLICT:
            return SATResult.UNSATISFIABLE

        literal_watch, clauses_literal_watched = self.initialize_watch_list()
        self.heuristics.initialize_scores(self.clauses)

        while not self.are_all_variables_assigned():  # While variables remain to assign
            variable = self.heuristics.decide(self.assignment)  # Decide : Pick a variable

            self.assign(variable)
            conflict, literal_watch = self.two_watch_propagate(literal_watch, clauses_literal_watched, variable)

            while conflict != -1:
                self.heuristics.conflict(conflict)

                learned_clause = self.analyze_conflict()  # Diagnose Conflict

                self.learn_clauses(literal_watch, clauses_literal_watched, learned_clause)
                self.statistics.increment_learned_counter()

                self.statistics.update_implications_counter(self.calculate_implications())

                jump_status, var = self.backjump()

                if jump_status == Status.FAILED:
                    return SATResult.UNSATISFIABLE
                self.assignment.append(var)
                conflict, literal_watch = self.two_watch_propagate(literal_watch, clauses_literal_watched, var)

    def calculate_implications(self):
        return self.statistics.implications_counter + len(self.assignment) - len(self.decision_levels)

    def unit_propagation(self):
        implication_found = True
        while implication_found:
            implication_found = False

            new_clauses = self.clauses

            for clause in self.clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    status, new_clauses = self.boolean_constraint_propagation(new_clauses, unit)
                    self.assignment.append(unit)
                    implication_found = True
                    if status == Status.CONFLICT:
                        return status

                self.clauses = new_clauses

                if not new_clauses:
                    return Status.CONFLICT

        return Status.SUCCESS

    @staticmethod
    def boolean_constraint_propagation(clauses, literal):
        new_clauses = [clause for clause in clauses]
        for clause in reversed(new_clauses):
            if literal in clause:
                new_clauses.remove(clause)
            if -literal in clause:
                clause.remove(-literal)
                if not clause:
                    return Status.CONFLICT, []
        return Status.SUCCESS, new_clauses

    def initialize_watch_list(self):
        literal_watch = {literal: [] for literal in range(-self.total_variables, self.total_variables + 1)}

        clauses_literal_watched = []

        for clause_index, clause in enumerate(self.clauses):
            unassigned_literals = [lit for lit in clause if lit not in self.assignment]

            if len(unassigned_literals) < 2:
                continue

            watched_literals = unassigned_literals[:2]

            clauses_literal_watched.append(watched_literals)

            for lit in watched_literals:
                literal_watch[lit].append(clause_index)

        return literal_watch, clauses_literal_watched

    def are_all_variables_assigned(self):
        return True if len(self.assignment) >= self.total_variables else False

    def assign(self, variable):
        self.decision_levels.append(len(self.assignment))

        self.statistics.increment_decision_counter()

        self.assignment.append(variable)

    def two_watch_propagate(self, literal_watch, clauses_literal_watched, variable):
        propagation_queue = [variable]
        while len(propagation_queue) != 0:
            variable = propagation_queue.pop()

            for affected_claus_num in reversed(literal_watch[-variable]):
                affected_claus = self.clauses[affected_claus_num]
                watched_clauses = Pair(clauses_literal_watched[affected_claus_num][0],
                                       clauses_literal_watched[affected_claus_num][1])

                previously_watched_clauses = watched_clauses
                status, watched_clauses, unit = self.check_status(affected_claus, watched_clauses)
                if status == ClauseStatus.UNIT:
                    propagation_queue.append(unit)
                    self.assignment.append(unit)
                elif status == ClauseStatus.UNSATISFIED:
                    return affected_claus, literal_watch

                for _, value in previously_watched_clauses._asdict().items():
                    literal_watch[value].remove(affected_claus_num)

                for index, (_, clause_value) in enumerate(watched_clauses._asdict().items()):
                    clauses_literal_watched[affected_claus_num][index] = clause_value
                    literal_watch[clause_value].append(affected_claus_num)

        return -1, literal_watch

    def check_status(self, clause, watched_clauses):
        unit = 0
        if watched_clauses.first in self.assignment or watched_clauses.second in self.assignment:
            return ClauseStatus.SATISFIED, watched_clauses, unit
        unassigned_literals = []
        for literal in clause:
            if -literal not in self.assignment:
                unassigned_literals.append(literal)
            if literal in self.assignment:
                clauses_to_watch = self.determine_clauses_to_watch(literal, watched_clauses)

                return ClauseStatus.SATISFIED, clauses_to_watch, unit
        if len(unassigned_literals) == 1:
            return ClauseStatus.UNIT, watched_clauses, unassigned_literals[0]
        if len(unassigned_literals) == 0:
            return ClauseStatus.UNSATISFIED, watched_clauses, unit
        else:
            return ClauseStatus.UNRESOLVED, Pair(unassigned_literals[0], unassigned_literals[1]), unit

    def determine_clauses_to_watch(self, literal, watched_clauses):
        if -watched_clauses.first not in self.assignment:
            return Pair(watched_clauses.first, literal)

        return Pair(literal, watched_clauses.second)

    def analyze_conflict(self):
        learn = []
        for level in self.decision_levels:
            learn.append(-self.assignment[level])
        return learn

    def learn_clauses(self, literal_watch, clauses_literal_watched, learned_clause):
        if len(learned_clause) == 1:
            self.assignment.append(learned_clause[0])

        if len(learned_clause) > 1:
            self.clauses.append(learned_clause)
            learned_clauses = [learned_clause[0], learned_clause[1]]
            clauses_literal_watched.append(learned_clauses)
            index = len(self.clauses) - 1

            for item in learned_clauses:
                literal_watch[item].append(index)

    def backjump(self):
        if not self.decision_levels:
            return Status.FAILED, -1

        decision_level = self.decision_levels.pop()
        literal = self.assignment[decision_level]
        del self.assignment[decision_level:]
        return Status.SUCCESS, -literal


if __name__ == "__main__":
    clauses, num_var = read_dimacs_file('../examples/sudoku5.cnf')

    start_time = time.process_time()

    sat_solver = CDCLSatSolver(clauses, num_var, CHBHeuristics())
    solution = sat_solver.solve()

    end_time = time.process_time()

    print("Statistics :")
    print("=============================================")
    print(sat_solver.statistics)
    print("=============================================")

    print("Elapsed time: " + str(end_time - start_time) + " sec")

    print(f'Status: {solution}')
    if solution == SATResult.SATISFIABLE:
        print(pretty_matrix(from_list_to_matrix(sat_solver.assignment)))
