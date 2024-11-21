import csv
import time
from collections import defaultdict, ChainMap, namedtuple
from copy import deepcopy
from multiprocessing import Pool

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, CDCLResult, SATResult
from Scripts.experiments.convert_soduko_to_cnf import sudoku_input_to_dimacs
from Scripts.experiments.sudoku_validator import is_valid_sudoku
from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_list_to_matrix, from_dict_to_matrix
from Scripts.heuristics.CHB import CHBHeuristics
from Scripts.heuristics.VSIDS import VSIDSHeuristics
from Scripts.simple_dpll import dpll

solutions = defaultdict()

CDCLResultWrapper = namedtuple('CDCLResultWrapper', ['result', 'elapsed_time'])
DPLLResultWrapper = namedtuple('DPLLResultWrapper',
                               ['is_satisfiable', 'assignment', 'statistics', 'elapsed_time'])


def solve_sudoku_with_vsids(clauses, total_variables, unsolved_sudoku):
    print(f'CDCL {VSIDS_PREFIX} - {unsolved_sudoku}')
    return solve_with_cdcl(clauses, total_variables, VSIDSHeuristics())


def solve_sudoku_with_chb(clauses, total_variables, unsolved_sudoku):
    print(f'CDCL {CHB_PREFIX} - {unsolved_sudoku}')
    return solve_with_cdcl(clauses, total_variables, CHBHeuristics())


def solve_with_cdcl(clauses, total_variables, heuristics):
    sat_solver = CDCLSatSolver(clauses, total_variables, heuristics)

    start_time = time.process_time()
    result = sat_solver.solve()
    end_time = time.process_time()

    return CDCLResultWrapper(result, end_time - start_time)


def solve_sudoku_with_basic_dpll(clauses, unsolved_sudoku):
    print(f'{DPLL_PREFIX} - {unsolved_sudoku}')
    statistics = {
        'implications': 0,
        'decisions': 0,
        'backtracks': 0,
        'recursions': 0,
        'conflicts': 0,
        'clause_simplifications': 0,
        'pure_literals': 0,
    }

    start_time = time.process_time()
    is_satisfiable, assignment, statistics = dpll(clauses, statistics, {})
    end_time = time.process_time()

    return DPLLResultWrapper(is_satisfiable, assignment, statistics, end_time - start_time)


def cdcl_results_to_dict(result: CDCLResult, elapsed_time, prefix):
    statistics = add_prefix(vars(result.statistics), prefix)

    statistics[f'{prefix}_is_solution_valid'] = is_valid_sudoku(from_list_to_matrix(result.solution))
    statistics[f'{prefix}_is_satisfied'] = result.status == SATResult.SATISFIABLE
    statistics[f'{prefix}_elapsed_time'] = elapsed_time

    return statistics


def add_prefix(dictionary: dict, prefix: str):
    return {prefix + '_' + key: value for key, value in dictionary.items()}


def solve_sudoku(unsolved_sudoku):
    unsolved_sudoku = unsolved_sudoku.strip()
    print(f'solving sudoku {unsolved_sudoku}')

    clauses = sudoku_input_to_dimacs(unsolved_sudoku) + sudoku_rules

    dpll_result: DPLLResultWrapper = solve_sudoku_with_basic_dpll(deepcopy(clauses), unsolved_sudoku)

    vsids_result = solve_sudoku_with_vsids(deepcopy(clauses), total_variables, unsolved_sudoku)
    vsids_dict = cdcl_results_to_dict(vsids_result.result, elapsed_time=vsids_result.elapsed_time, prefix=VSIDS_PREFIX)

    chb_result = solve_sudoku_with_chb(deepcopy(clauses), total_variables, unsolved_sudoku)
    chb_dict = cdcl_results_to_dict(chb_result.result, elapsed_time=chb_result.elapsed_time, prefix=CHB_PREFIX)

    dpll_dict = add_prefix(dpll_result.statistics, DPLL_PREFIX)
    dpll_dict[f'{DPLL_PREFIX}_is_satisfied'] = dpll_result.is_satisfiable
    dpll_dict[f'{DPLL_PREFIX}_is_solution_valid'] = is_valid_sudoku(from_dict_to_matrix(dpll_result.assignment))
    dpll_dict[f'{DPLL_PREFIX}_elapsed_time'] = dpll_result.elapsed_time

    final_dict = ChainMap(vsids_dict, chb_dict, dpll_dict)
    final_dict[UNSOLVED_SUDOKU_PREFIX] = unsolved_sudoku
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_number_of_clues'] = 81 - unsolved_sudoku.count('.')
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_number_of_unknown_positions'] = unsolved_sudoku.count('.')
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_total_of_characters'] = len(unsolved_sudoku)

    print(f'Finished sudoku {unsolved_sudoku}')
    return dict(final_dict)


def merge(data: list[dict]):
    keys = set().union(*data)
    return {
        key: [dictionary[key] for dictionary in data if key in dictionary]
        for key in keys
    }


def main(args):
    # with semaphore:
    with Pool() as pool:
        results = pool.map(solve_sudoku, args)

        data = merge(results)

        sorted_data = dict(sorted(data.items(), key=lambda x: x[0].lower()))

        print('Storing results')
        with open(OUTPUT_PATH, 'w', newline='') as file:
            writer = csv.DictWriter(file, sorted_data.keys())
            writer.writeheader()
            rows = zip(*sorted_data.values())
            writer.writerows(dict(zip(sorted_data.keys(), row)) for row in rows)


def get_unsolved_sudokus(file_path):
    with open(file_path, 'r') as file:
        return set(file.readlines())


VSIDS_PREFIX = 'VSIDS'
CHB_PREFIX = 'CHB'
DPLL_PREFIX = 'basic_DPLL'
UNSOLVED_SUDOKU_PREFIX = 'unsolved_sudoku'

OUTPUT_PATH = 'experiment_result_9x9_fixed.csv'
SUDOKU_DATASET_FILE_PATH = '../../test_sets/all_9x9.txt'

SUDOKU_RULES = '../../sudoku_rules/sudoku-rules-9x9.cnf'
sudoku_rules, total_variables = read_dimacs_file(SUDOKU_RULES)

if __name__ == "__main__":
    unsolved_sudokus = list(get_unsolved_sudokus(SUDOKU_DATASET_FILE_PATH))
    start = time.perf_counter()
    main(unsolved_sudokus)
    end = time.perf_counter() - start
    print(f"Program finished in {end:0.2f} seconds to solve {len(unsolved_sudokus)} sudokus.")
