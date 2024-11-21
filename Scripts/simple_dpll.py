import sys
import time

from Scripts.helpers.dimacs_reader import read_dimacs_file
from Scripts.helpers.sat_outcome_converter import from_dict_to_matrix, pretty_matrix
def unit_propagation(clauses, assignment, statistics):
    """
    Perform unit propagation until no unit clauses remain.
    """
    while True:
        unit_clauses = [clause[0] for clause in clauses if len(clause) == 1]
        if not unit_clauses:
            break
        for unit in unit_clauses:
            value = unit > 0
            assignment[abs(unit)] = value
            statistics['implications'] += 1
            statistics['clause_simplifications'] += len([clause for clause in clauses if unit in clause])
            result = simplify_clauses(clauses, unit)
            if result is False:
                statistics['conflicts'] += 1
                return False, assignment
            clauses = result
    return clauses, assignment


def simplify_clauses(clauses, literal):
    """
    Simplify the clauses by removing those satisfied by the literal
    and updating others to exclude the negated literal.
    """
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue  # Clause is satisfied
        new_clause = [x for x in clause if x != -literal]  # Remove negated literal
        if not new_clause:  # If a clause becomes empty, a conflict occurred
            return False
        new_clauses.append(new_clause)
    return new_clauses


def find_pure_literals(clauses):
    """
    Find all pure literals in the current set of clauses.
    """
    counts = {}
    for clause in clauses:
        for literal in clause:
            counts[literal] = counts.get(literal, 0) + 1
    return [lit for lit in counts if -lit not in counts]


def apply_pure_literals(clauses, assignment, statistics):
    """
    Assign pure literals to satisfy their corresponding clauses.
    """
    pure_literals = find_pure_literals(clauses)
    for pure in pure_literals:
        assignment[abs(pure)] = pure > 0
        statistics['implications'] += 1
        statistics['clause_simplifications'] += len([clause for clause in clauses if pure in clause])

        result = simplify_clauses(clauses, pure)
        if result is False:
            statistics['conflicts'] += 1
            return False, assignment, clauses
        clauses = result
    return clauses, assignment, pure_literals


def select_variable(clauses, assignment, statistics):
    """
    Choose the next variable to assign using a simple heuristic.
    """
    for clause in clauses:
        for literal in clause:
            if abs(literal) not in assignment:
                statistics['decisions'] += 1
                return abs(literal)
    return None  # No unassigned variables


def dpll_recursive(clauses, assignment, statistics):
    """
    Recursively attempt to solve the SAT problem using the DPLL algorithm.
    """
    statistics['recursions'] += 1

    # Base case: All clauses are satisfied
    if not clauses:
        return True, assignment, statistics

    # Base case: A clause is unsatisfiable (empty clause exists)
    if any(len(clause) == 0 for clause in clauses):
        statistics['conflicts'] += 1
        return False, {}, statistics

    # Step 1: Perform Unit Propagation
    clauses, assignment = unit_propagation(clauses, assignment, statistics)
    if clauses is False:
        return False, assignment, statistics

    # Step 2: Apply Pure Literal Elimination
    clauses, assignment, pure_literals = apply_pure_literals(clauses, assignment, statistics)
    if clauses is False:
        return False, assignment, statistics

    # Step 3: Choose a variable to branch on
    variable = select_variable(clauses, assignment, statistics)
    if variable is None:
        # Edge case: All variables assigned but no satisfying assignment found
        satisfied = all(
            any(literal if literal > 0 else not assignment[abs(literal)] for literal in clause)
            for clause in clauses
        )
        return satisfied, assignment, statistics

    # Step 4: Recursively try True and False assignments for the selected variable
    for value in [True, False]:
        new_assignment = assignment.copy()
        new_assignment[variable] = value
        result, final_assignment, statistics = dpll_recursive(
            simplify_clauses(clauses, variable if value else -variable),
            new_assignment,
            statistics,
        )
        if result:
            return True, final_assignment, statistics

        # Update statistics for backtracking
        statistics['backtracks'] += 1

    # If both branches fail, return unsatisfiable
    return False, assignment, statistics


def dpll(clauses, statistics, assignment={}):
    """
    Wrapper function for the DPLL algorithm.
    """
    return dpll_recursive(clauses, assignment, statistics)


def save_output(filepath, satisfiable, assignment, grid_size=9):
    """
    Save the SAT solving results to an output file and a readable Sudoku format.
    """
    output_file = filepath + ".out"
    sudoku_file = filepath.replace(".cnf", ".txt")

    # Write the SAT result to the output file
    with open(output_file, "w") as file:
        file.write("SATISFIABLE\n" if satisfiable else "UNSATISFIABLE\n")
        if satisfiable:
            file.write(" ".join(str(var if value else -var) for var, value in sorted(assignment.items())))
            file.write(" 0\n")

    # If satisfiable, generate the Sudoku matrix and save it
    if satisfiable:
        sudoku_matrix = from_dict_to_matrix(assignment)  # Use helper to create Sudoku grid
        sudoku_string = pretty_matrix(sudoku_matrix)  # Format the matrix into a string

        with open(sudoku_file, "w") as sudoku_file:
            sudoku_file.write(sudoku_string)

        # Display the Sudoku grid for confirmation
        print("Sudoku solution:")
        print(sudoku_string)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sat_solver.py <rulesfilepath> <puzzlefilepath>")
        sys.exit(1)

    rules_file_path = sys.argv[1]
    puzzle_file_path = sys.argv[2]

    # Load DIMACS files
    rules_clauses, _ = read_dimacs_file(rules_file_path)
    puzzle_clauses, _ = read_dimacs_file(puzzle_file_path)

    # Combine rules and puzzle clauses
    combined_clauses = rules_clauses + puzzle_clauses

    statistics = {
        'implications': 0,
        'decisions': 0,
        'backtracks': 0,
        'recursions': 0,
        'conflicts': 0,
        'clause_simplifications': 0,
        'pure_literals': 0,
    }

    # Solve the SAT problem
    start = time.time()
    satisfiable, assignment, statistics = dpll(combined_clauses, statistics, {})
    end = time.time()

    # Save the results and display them
    save_output('../examples/sudoku1.cnf', satisfiable, assignment, grid_size=9)
    print(f"Result: {'SATISFIABLE' if satisfiable else 'UNSATISFIABLE'}")
    print(f"Execution Time: {end - start:.4f} seconds")
    print("Solver Statistics:", statistics)