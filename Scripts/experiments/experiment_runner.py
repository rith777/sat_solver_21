import csv
import time
from collections import defaultdict, ChainMap, namedtuple
from copy import deepcopy
from enum import Enum
from multiprocessing import Pool

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, SATResult
from Scripts.experiments.convert_soduko_to_cnf import sudoku_input_to_dimacs
from Scripts.experiments.sudoku_validator import is_valid_sudoku
from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_list_to_matrix, from_dict_to_matrix
from Scripts.heuristics.CHB import CHBHeuristics
from Scripts.heuristics.VSIDS import VSIDSHeuristics
from Scripts.simple_dpll import dpll

solutions = defaultdict()

CDCLResultWrapper = namedtuple('CDCLResultWrapper', ['result', 'history', 'elapsed_time'])
DPLLResultWrapper = namedtuple('DPLLResultWrapper',
                               ['is_satisfiable', 'assignment', 'statistics', 'elapsed_time'])

CDCLHistory = namedtuple('CDCLHistory', ['unsolved_sudoku', 'chb', 'vsids'])


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

    return CDCLResultWrapper(result, sat_solver.historyManager.history, end_time - start_time)


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


def cdcl_results_to_dict(result: CDCLResultWrapper, matrix_length, prefix):
    sat_solver_result = result.result

    statistics = add_prefix(vars(sat_solver_result.statistics), prefix)

    sudoku_matrix = from_list_to_matrix(sat_solver_result.solution, matrix_length)
    statistics[f'{prefix}_is_solution_valid'] = is_valid_sudoku(sudoku_matrix)
    statistics[f'{prefix}_is_satisfied'] = sat_solver_result.status == SATResult.SATISFIABLE
    statistics[f'{prefix}_elapsed_time'] = result.elapsed_time

    return statistics


def add_prefix(dictionary: dict, prefix: str):
    return {prefix + '_' + key: value for key, value in dictionary.items()}


def solve_sudoku(unsolved_sudoku):
    unsolved_sudoku = unsolved_sudoku.strip()
    print(f'solving sudoku {unsolved_sudoku}')

    clauses = sudoku_input_to_dimacs(unsolved_sudoku) + sudoku_rules

    dpll_result: DPLLResultWrapper = solve_sudoku_with_basic_dpll(deepcopy(clauses), unsolved_sudoku)

    chb_result = solve_sudoku_with_chb(deepcopy(clauses), total_variables, unsolved_sudoku)
    vsids_result = solve_sudoku_with_vsids(deepcopy(clauses), total_variables, unsolved_sudoku)
    vsids_dict = cdcl_results_to_dict(vsids_result, matrix_length, prefix=VSIDS_PREFIX)

    chb_dict = cdcl_results_to_dict(chb_result, matrix_length, prefix=CHB_PREFIX)

    dpll_dict = add_prefix(dpll_result.statistics, DPLL_PREFIX)
    dpll_dict[f'{DPLL_PREFIX}_is_satisfied'] = dpll_result.is_satisfiable

    dpll_sudoku_matrix = from_dict_to_matrix(dpll_result.assignment, matrix_length)
    dpll_dict[f'{DPLL_PREFIX}_is_solution_valid'] = is_valid_sudoku(dpll_sudoku_matrix)
    dpll_dict[f'{DPLL_PREFIX}_elapsed_time'] = dpll_result.elapsed_time

    final_dict = ChainMap(vsids_dict, chb_dict, dpll_dict)
    final_dict[UNSOLVED_SUDOKU_PREFIX] = unsolved_sudoku
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_number_of_clues'] = 81 - unsolved_sudoku.count('.')
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_number_of_unknown_positions'] = unsolved_sudoku.count('.')
    final_dict[f'{UNSOLVED_SUDOKU_PREFIX}_total_of_characters'] = len(unsolved_sudoku)

    print(f'Finished sudoku {unsolved_sudoku}')
    return dict(final_dict), CDCLHistory(unsolved_sudoku, chb_result.history, vsids_result.history)


def merge(data: list[dict]):
    keys = set().union(*data)
    return {
        key: [dictionary[key] for dictionary in data if key in dictionary]
        for key in keys
    }


def main(args):
    with Pool() as pool:
        results = pool.map(solve_sudoku, args)

        data = merge([result[0] for result in results])

        sorted_data = dict(sorted(data.items(), key=lambda x: x[0].lower()))

        cdcl_history = [result[1] for result in results]

        print('Storing metric results')
        with open(OUTPUT_PATH, 'w', newline='') as file:
            writer = csv.DictWriter(file, sorted_data.keys())
            writer.writeheader()
            rows = zip(*sorted_data.values())
            writer.writerows(dict(zip(sorted_data.keys(), row)) for row in rows)

        print('Storing history results')
        with open("cbh_history.csv", 'w', newline='') as chb_history_file, open("vsids_history.csv", 'w',
                                                                                newline='') as visids_history_file:
            chb_history_writer = csv.DictWriter(chb_history_file, ['sudoku', 'event_type', 'count', 'datetime'])
            chb_history_writer.writeheader()

            vsids_history_writer = csv.DictWriter(visids_history_file, ['sudoku', 'event_type', 'count', 'datetime'])
            vsids_history_writer.writeheader()

            for item in cdcl_history:
                for event in item.chb:
                    dictionary = event.to_dict()
                    dictionary['sudoku'] = event.event_type = item.unsolved_sudoku
                    chb_history_writer.writerow(dictionary)

                for event in item.vsids:
                    dictionary = event.to_dict()
                    dictionary['sudoku'] = event.event_type = item.unsolved_sudoku
                    vsids_history_writer.writerow(dictionary)


def get_unsolved_sudokus(file_path):
    with open(file_path, 'r') as file:
        return set(file.readlines())


class SudokuType(Enum):
    SUDOKU_4_BY_4 = 1
    SUDOKU_9_BY_9 = 2
    SUDOKU_16_BY_16 = 3


def load_sudoku_setup_based_on(sudoku_type: SudokuType):
    matrix_length, rule_file_path = None, None

    if sudoku_type == SudokuType.SUDOKU_4_BY_4:
        matrix_length = 4
        rule_file_path = '../../sudoku_rules/sudoku-rules-4x4.cnf'

    if sudoku_type == SudokuType.SUDOKU_9_BY_9:
        matrix_length = 9
        rule_file_path = '../../sudoku_rules/sudoku-rules-9x9.cnf'

    if sudoku_type == SudokuType.SUDOKU_16_BY_16:
        matrix_length = 16
        rule_file_path = '../../sudoku_rules/sudoku-rules-16x16.cnf'

    return matrix_length, rule_file_path


VSIDS_PREFIX = 'VSIDS'
CHB_PREFIX = 'CHB'
DPLL_PREFIX = 'basic_DPLL'
UNSOLVED_SUDOKU_PREFIX = 'unsolved_sudoku'

OUTPUT_PATH = 'experiment_result_9x9_final_with_history.csv'

SUDOKU_DATASET_FILE_PATH = '../../test_sets/all_9x9.txt'

matrix_length, rule_file_path = load_sudoku_setup_based_on(SudokuType.SUDOKU_9_BY_9)
sudoku_rules, total_variables = read_dimacs_file(rule_file_path)

if __name__ == "__main__":
    unsolved_sudokus = list(get_unsolved_sudokus(SUDOKU_DATASET_FILE_PATH))
    start = time.perf_counter()
    main(unsolved_sudokus)
    end = time.perf_counter() - start
    print(f"Program finished in {end:0.2f} seconds to solve {len(unsolved_sudokus)} sudokus.")
