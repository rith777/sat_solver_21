import asyncio
import csv
import time
from collections import defaultdict, ChainMap

import aiofiles
from aiocsv import AsyncWriter

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, CDCLResult, SATResult
from Scripts.experiments.convert_soduko_to_cnf import sudoku_string_to_cnf_clauses
from Scripts.heuristics.CHB import CHBHeuristics
from Scripts.heuristics.VSIDS import VSIDSHeuristics
from Scripts.simple_dpll import dpll

solutions = defaultdict()


async def sudoku_to_cnf(unsolved_sudoku):
    return sudoku_string_to_cnf_clauses(unsolved_sudoku.strip())


async def solve_sudoku_with_vsids(clauses, total_variables):
    return await solve_with_cdcl(clauses, total_variables, VSIDSHeuristics())


async def solve_sudoku_with_chb(clauses, total_variables):
    return await solve_with_cdcl(clauses, total_variables, CHBHeuristics())


async def solve_with_cdcl(clauses, total_variables, heuristics):
    sat_solver = CDCLSatSolver(clauses, total_variables, heuristics)

    return await asyncio.to_thread(sat_solver.solve)


async def solve_sudoku_with_basic_dpll(clauses):
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

    return await asyncio.to_thread(dpll, clauses, statistics, {})


async def cdcl_results_to_dict(result: CDCLResult, prefix, is_valid_solution):
    statistics = add_prefix(vars(result.statistics), prefix)

    statistics[f'{prefix}_is_solution_valid'] = is_valid_solution
    statistics[f'{prefix}_is_satisfied'] = result.status == SATResult.SATISFIABLE
    statistics[f'{prefix}_elapsed_time'] = result.statistics.end_time - result.statistics.start_time

    return statistics


def add_prefix(dictionary: dict, prefix: str):
    return {prefix + '_' + key: value for key, value in dictionary.items()}


async def solve_sudoku(unsolved_sudoku):
    print(f'solving sudoku {unsolved_sudoku}')

    clauses, total_variables = await sudoku_to_cnf(unsolved_sudoku)

    vsids_result = await solve_sudoku_with_vsids(clauses, total_variables)

    chb_result = await solve_sudoku_with_chb(clauses, total_variables)

    is_satisfied, assignment, statistics = await solve_sudoku_with_basic_dpll(clauses)

    vsids_dict = await cdcl_results_to_dict(vsids_result, prefix=VSIDS_PREFIX, is_valid_solution=True)
    chb_dict = await cdcl_results_to_dict(chb_result, prefix=CHB_PREFIX, is_valid_solution=True)
    dpll_dict = add_prefix(statistics, DPLL_PREFIX)
    dpll_dict[f'{DPLL_PREFIX}_is_satisfied'] = is_satisfied

    final_dict = ChainMap(vsids_dict, chb_dict, dpll_dict)
    final_dict['unsolved_sudoku'] = unsolved_sudoku
    final_dict['number_of_clues'] = 81 - unsolved_sudoku.count('.')

    return dict(final_dict)


async def save_output(data: dict):
    with open(OUTPUT_PATH, 'w', newline="") as file:
        writer = csv.DictWriter(file, data.keys())
        writer.writeheader()
        writer.writerows(data)


def merge(data: list[dict]):
    keys = set().union(*data)
    return {
        key: [dictionary[key] for dictionary in data if key in dictionary]
        for key in keys
    }


async def main(*args):
    responses = await asyncio.gather(*(solve_sudoku(unsolved_sudoku) for unsolved_sudoku in args))
    r = merge(responses)

    async with aiofiles.open('output.csv', 'w') as file:
        writer = AsyncWriter(file, )
        await writer.writerow(r.keys())
        await writer.writerows(zip(*r.values()))


def get_unsolved_sudokus(file_path):
    with open('../../test_sets/top2365.sdk.txt', 'r') as file:
        return file.readlines()


VSIDS_PREFIX = 'VSIDS'
CHB_PREFIX = 'CHB'
DPLL_PREFIX = 'basic_DPLL'
OUTPUT_PATH = 'experiment_result.csv'
SUDOKU_DATASET_FILE_PATH = '../../test_sets/top91.sdk.txt'

if __name__ == "__main__":
    unsolved_sudokus = get_unsolved_sudokus(SUDOKU_DATASET_FILE_PATH)
    start = time.perf_counter()
    asyncio.run(main(*unsolved_sudokus))
    end = time.perf_counter() - start
    print(f"Program finished in {end:0.2f} seconds to solve {len(unsolved_sudokus)} sudokus.")
