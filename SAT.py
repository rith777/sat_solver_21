#!bin/bash

import pprint
import sys

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, SATResult
from Scripts.experiments.sudoku_validator import is_valid_sudoku
from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_dict_to_matrix, pretty_matrix, from_list_to_matrix
from Scripts.heuristics.CHB import CHBHeuristics
from Scripts.heuristics.VSIDS import VSIDSHeuristics
from Scripts.simple_dpll import dpll

DPLL_STRATEGY = 1
CDCL_CHB_STRATEGY = 2
CDCL_VISIDS_STRATEGY = 3


def solve_with_dpll(clauses):
    statistics = {
        'implications': 0,
        'decisions': 0,
        'backtracks': 0,
        'recursions': 0,
        'conflicts': 0,
        'clause_simplifications': 0,
        'pure_literals': 0,
        'start': None
    }

    is_satisfied, assignment, statistics = dpll(clauses, statistics)

    if is_satisfied:
        print("SATISFIED")
        sudoku_matrix = from_dict_to_matrix(assignment)  # Use helper to create Sudoku grid

        print("Statistics:")
        print("=============================================")
        print(pprint.pp(statistics))
        print("=============================================")

        print("Solution:")
        print("=============================================")
        print(pretty_matrix(sudoku_matrix))
        print("=============================================")
        print(f"is sudoku matrix valid? {is_valid_sudoku(sudoku_matrix)}")
    else:
        print("UNSATISFIED")


def solve_with_cdcl(clauses, total_variables, heuristics):
    results = CDCLSatSolver(clauses, total_variables, heuristics).solve()

    print(f'Status: {results.status}')

    if results.status == SATResult.SATISFIABLE:
        print("Statistics :")
        print("=============================================")
        print(results.statistics)
        print("=============================================")

        sudoku_matrix = from_list_to_matrix(results.solution)
        print("Solution:")
        print("=============================================")
        print(pretty_matrix(sudoku_matrix))
        print("=============================================")
        print(f"is sudoku matrix valid? {is_valid_sudoku(sudoku_matrix)}")



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: SAT -Sn inputfile")
        sys.exit(1)

    strategy = sys.argv[1]

    if not strategy.startswith("-S") or not strategy[2:].isdigit() or int(strategy[2:]) > 3 or int(strategy[2:]) == 0:
        print("Error: Strategy should be specified as '-Sn', where n is 1 (DPLL), 2 (CDCL - CHB), or 3 (CDCL - VSIDS)")
        sys.exit(1)

    file_path = sys.argv[2]

    clauses, num_var = read_dimacs_file(file_path)

    # Assuming rules file is passed as another argument
    # Load the rules file (you may need to modify this to handle a separate rules file)
    rules_file_path = "C:\github\sat_solver\sat_solver_21\sudoku_rules\sudoku-rules-9x9.cnf"  # Specify the correct path to the rules file
    rules_clauses, num_var_rules = read_dimacs_file(rules_file_path)

    # Combine the clauses from the rules file and the puzzle file
    combined_clauses = rules_clauses + clauses  # Combine both sets of clauses

    strategy_number = int(strategy[2:])

    if strategy_number == DPLL_STRATEGY:
        print('Solving sudoku with basic DPLL...\n\n')
        solve_with_dpll(combined_clauses)

    elif strategy_number == CDCL_CHB_STRATEGY:
        print('Solving sudoku with CDCL using CHB heuristics...\n\n')
        solve_with_cdcl(combined_clauses, num_var, CHBHeuristics())

    elif strategy_number == CDCL_VISIDS_STRATEGY:
        print('Solving sudoku with CDCL using VSIDS heuristics...\n\n')
        solve_with_cdcl(combined_clauses, num_var, VSIDSHeuristics())


