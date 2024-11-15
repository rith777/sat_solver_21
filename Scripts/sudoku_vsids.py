import time

from Scripts.cdcl_heuristics_solver import CDCLSatSolver, SATResult
from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_list_to_matrix, pretty_matrix
from Scripts.heuristics.VSIDS import VSIDSHeuristics

if __name__ == "__main__":
    clauses, num_var = read_dimacs_file('../examples/sudoku5.cnf')

    start_time = time.process_time()

    sat_solver = CDCLSatSolver(clauses, num_var, VSIDSHeuristics())
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
