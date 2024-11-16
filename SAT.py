#!bin/bash

import pprint
import sys

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, SATResult
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
    else:
        print("UNSATISFIED")


def solve_with_cdcl(clauses, total_variables, heuristics):
    results = CDCLSatSolver(clauses, total_variables, heuristics).solve()

    print(f'Status: {results.status}')

    print("Statistics :")
    print("=============================================")
    print(results.statistics)
    print("=============================================")

    # print("Elapsed time: " + str(end_time - start_time) + " sec")

    if results.status == SATResult.SATISFIABLE:
        print(pretty_matrix(from_list_to_matrix(results.solution)))


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

    strategy_number = int(strategy[2:])
    if strategy_number == DPLL_STRATEGY:
        print('Solving sudoky with basic DPLL...\n\n')
        solve_with_dpll(clauses)
    if strategy_number == CDCL_CHB_STRATEGY:
        print('Solving sudoky with CDCL using CHB heuristics...\n\n')
        solve_with_cdcl(clauses, num_var, CHBHeuristics())

    if strategy_number == CDCL_VISIDS_STRATEGY:
        print('Solving sudoky with CDCL using VSIDS heuristics...\n\n')
        solve_with_cdcl(clauses, num_var, VSIDSHeuristics())
