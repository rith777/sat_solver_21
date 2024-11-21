from collections import namedtuple, defaultdict
from dataclasses import dataclass
from enum import Enum, auto

from Scripts.experiments.History import HistoryManager

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
        self.successful_backjumps_counter = 0
        self.failed_backjumps_counter = 0
        self.conflicts_counter = 0

    def increment_learned_counter(self):
        self.learned_counter += 1

    def increment_decision_counter(self):
        self.decision_counter += 1

    def update_implications_counter(self, new_value):
        self.implications_counter = new_value

    def increment_implications_counter(self):
        self.implications_counter += 1

    def increment_successful_backjumps_counter(self):
        self.successful_backjumps_counter += 1

    def increment_failed_backjumps_counter(self):
        self.failed_backjumps_counter += 1

    def increment_conflicts_counter(self):
        self.conflicts_counter += 1

    def __str__(self):
        return f"""
        Learned clauses: {self.learned_counter}
        Amount of decisions: {self.decision_counter}
        Amount of implications: {self.implications_counter}
        Amount of conflicts: {self.conflicts_counter}
        Amount of successful backjumps: {self.successful_backjumps_counter}
        Amount of failed backjumps: {self.failed_backjumps_counter}
        """


@dataclass(frozen=True)
class CDCLResult:
    solution: list[int]
    status: SATResult
    statistics: Statistics


class CDCLSatSolver:
    def __init__(self, clauses, total_variables, heuristics):
        self.clauses = clauses
        self.total_variables = total_variables
        self.assignment = []
        self.decision_levels = []

        self.heuristics = heuristics
        self.statistics = Statistics()

        self.literal_watch = defaultdict(list)
        self.clauses_literal_watched = defaultdict(list)

        self.historyManager = HistoryManager()

    def solve(self):

        self.unit_propagation()
        if self.clauses == Status.CONFLICT:
            return CDCLResult(self.assignment, SATResult.UNSATISFIABLE, self.statistics)

        self.initialize_watch_list()
        self.heuristics.initialize_scores(self.clauses)

        while not self.are_all_variables_assigned():  # While variables remain to assign
            variable = self.heuristics.decide(self.assignment)  # Decide : Pick a variable

            ###added by rith!!!!
            if variable is None:
                # No variable to decide, meaning the solution is SAT
                return CDCLResult(self.assignment, SATResult.SATISFIABLE, self.statistics)

            self.assign(variable)
            conflict = self.two_watch_propagate(variable)

            while conflict != -1:
                self.heuristics.conflict(conflict)

                learned_clause = self.analyze_conflict()  # Diagnose Conflict

                self.learn_clauses(learned_clause)
                self.statistics.increment_learned_counter()

                self.statistics.update_implications_counter(self.calculate_implications())

                jump_status, variable = self.backjump()

                if jump_status == Status.FAILED:
                    return SATResult.UNSATISFIABLE
                self.assignment.append(variable)
                conflict = self.two_watch_propagate(variable)

        return CDCLResult(self.assignment, SATResult.SATISFIABLE, self.statistics)

    def calculate_implications(self):
        return self.statistics.implications_counter + len(self.assignment) - len(self.decision_levels)

    def unit_propagation(self):
        flag = True
        while flag:
            flag = False

            new_clauses = self.clauses

            for clause in self.clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    status, new_clauses = self.boolean_constraint_propagation(new_clauses, unit)
                    self.assignment.append(unit)
                    flag = True
                    if status == Status.CONFLICT:
                        self.on_conflict_found()
                        return status

                self.clauses = new_clauses

                if not new_clauses:
                    self.on_conflict_found()
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

    def on_conflict_found(self):
        self.statistics.increment_conflicts_counter()
        self.historyManager.add_conflict(self.statistics.conflicts_counter)

    def initialize_watch_list(self):
        for clause_index, clause in enumerate(self.clauses):
            unassigned_literals = [lit for lit in clause if lit not in self.assignment]

            if len(unassigned_literals) < 2:
                continue

            watched_literals = unassigned_literals[:2]

            self.clauses_literal_watched[clause_index] = watched_literals

            for lit in watched_literals:
                self.literal_watch[lit].append(clause_index)

        return self.literal_watch, self.clauses_literal_watched

    def are_all_variables_assigned(self):
        return True if len(self.assignment) >= self.total_variables else False

    def assign(self, variable):
        self.decision_levels.append(len(self.assignment))

        self.statistics.increment_decision_counter()

        self.assignment.append(variable)

    def two_watch_propagate(self, variable):
        propagation_queue = [variable]
        while len(propagation_queue) != 0:
            variable = propagation_queue.pop()

            for affected_clause_num in reversed(self.literal_watch[-variable]):
                affected_clause = self.clauses[affected_clause_num]
                watched_clauses = Pair(self.clauses_literal_watched[affected_clause_num][0],
                                       self.clauses_literal_watched[affected_clause_num][1])

                previously_watched_clauses = watched_clauses
                status, watched_clauses, unit = self.evaluate_clause_status(affected_clause, watched_clauses)
                if status == ClauseStatus.UNIT:
                    propagation_queue.append(unit)
                    self.assignment.append(unit)
                    self.statistics.increment_implications_counter()
                elif status == ClauseStatus.UNSATISFIED:
                    self.on_conflict_found()
                    return affected_clause

                for _, value in previously_watched_clauses._asdict().items():
                    self.literal_watch[value].remove(affected_clause_num)

                for index, (_, clause_value) in enumerate(watched_clauses._asdict().items()):
                    self.clauses_literal_watched[affected_clause_num][index] = clause_value
                    self.literal_watch[clause_value].append(affected_clause_num)

        return -1

    def evaluate_clause_status(self, clause, watched_clauses):
        unit = 0
        if self.are_watched_clauses_already_assigned(watched_clauses):
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

    def are_watched_clauses_already_assigned(self, watched_clauses):
        return watched_clauses.first in self.assignment or watched_clauses.second in self.assignment

    def determine_clauses_to_watch(self, literal, watched_clauses):
        if -watched_clauses.first not in self.assignment:
            return Pair(watched_clauses.first, literal)

        return Pair(literal, watched_clauses.second)

    def analyze_conflict(self):
        learn = []
        for level in self.decision_levels:
            learn.append(-self.assignment[level])
        return learn

    def learn_clauses(self, learned_clause):
        if len(learned_clause) == 1:
            self.assignment.append(learned_clause[0])

        if len(learned_clause) > 1:
            self.clauses.append(learned_clause)
            learned_clauses = learned_clause[:2]
            index = len(self.clauses) - 1
            self.clauses_literal_watched[index] = learned_clauses

            for item in learned_clauses:
                self.literal_watch[item].append(index)

    def backjump(self):
        if not self.decision_levels:
            self.statistics.increment_failed_backjumps_counter()
            return Status.FAILED, -1

        decision_level = self.decision_levels.pop()
        literal = self.assignment[decision_level]
        del self.assignment[decision_level:]

        self.statistics.increment_successful_backjumps_counter()
        return Status.SUCCESS, -literal
