import sys

from helpers.dimacs_reader import read_dimacs_file
from helpers.sat_outcome_converter import from_dict_to_cnf, from_dict_to_matrix, pretty_matrix


def unit_propagate(clauses, assign):
    """simplify clauses with unit propagation."""

    has_changes = True
    while has_changes:  # run until changes are found in list of clauses.
        has_changes = False
        unit_clauses = find_all_unit_literals_in(clauses)
        # processing unit clauses
        for unit in unit_clauses:
            assign[abs(unit)] = unit > 0  # setting var in unit clause to true or false

            new_clauses = [clause for clause in clauses if unit not in clause]

            clauses = new_clauses

            # Remove negation of unit clauses too (ex: removing p and not(p) if p is a literal)
            for clause in clauses:
                if -unit in clause:  # if negated unit clause in clause you can remove it from the clause
                    clause.remove(-unit)
            has_changes = True
    return clauses, assign  # return assignment and updated clauses without literal


def find_all_unit_literals_in(clauses):
    return [clause[0] for clause in clauses if len(clause) == 1]


def eliminate_pure_literal(clauses, assign):
    """assign values to pure literals"""
    literals = [literal for clause in clauses for literal in clause]

    # identifying pure lits and assigning truth valeus
    for literal in set(literals):
        if -literal not in literals:  # if negation absent it is pure (ex if p then not(p) should not be in lit for p to be pure)
            assign[abs(literal)] = literal > 0  # Set true or false for positive or negative pure lit
            # if it's a positive pure literal (ex p), we can assign it true
            # If it's a negative pure literal (ex, ¬p), we can assign its (p) to False

            new_clauses = [clause for clause in clauses if literal not in clause]
            clauses = new_clauses  # basically discards all clauses with the pure literal returns updated list of clauses
    return clauses, assign


def dpll_algorithm(clauses, assign):
    """DPLL algorithm"""

    # do unit propagation and pure lit elimination
    clauses, assign = unit_propagate(clauses, assign)
    clauses, assign = eliminate_pure_literal(clauses, assign)

    if not clauses:  # All clauses satisfied so return true (solution found!!!)
        return True, assign
    if any(len(clause) == 0 for clause in clauses):  # Found an unsatisfiable clause
        return False, {}

    unassigned = find_unassigned_literals(assign, clauses)
    # makes sure all vars are only picked once
    if not unassigned:  # if empty then it should be unsatisfiable
        return False, {}

    selected_var = unassigned[0]  # take the first one

    # Try assigning True to the selected variable
    updated_assign = assign.copy()
    updated_assign[selected_var] = True

    # recursive call with updated assignment of var and filter out clauses that selected var satisfies
    new_clauses = [clause for clause in clauses if selected_var not in clause]
    sat, result = dpll_algorithm(new_clauses, updated_assign)
    if not sat:
        # update assignment var as false and try the same recursive call
        updated_assign[selected_var] = False
        new_clauses = [clause for clause in clauses if -selected_var not in clause]
        sat, result = dpll_algorithm(new_clauses, updated_assign)
    return sat, result


def find_unassigned_literals(assign, clauses):
    return [abs(literal) for clause in clauses for literal in clause if abs(literal) not in assign]


def save_output(path, assign, satisfiable):
    """Write result to output file (ex filename.out)."""
    output_file = path + '.out'
    sudoku_path = path.replace(".cnf", ".txt")
    if satisfiable:
        with open(output_file, 'w') as output:
            output.write(" 0 \n".join(from_dict_to_cnf(assign)))

        with open(sudoku_path, mode='w') as sudoku:
            sudoku.write(pretty_matrix(from_dict_to_matrix(assign)))  # Write empty file for unsatisfiable


def solve_sudoku(clauses):
    assign = {}
    is_satisfiable, final_assignment = dpll_algorithm(clauses, assign)

    # Save the result to an output file based on the puzzle path
    save_output(puzzle_file_path, final_assignment, is_satisfiable)

    if is_satisfiable:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python DPLL_no_heuristics.py <rulesfilepath> <puzzlefilepath>")
    else:
        rules_file_path = sys.argv[1]
        puzzle_file_path = sys.argv[2]

        # Load rules and puzzle clauses
        rules_clauses, rules_var_count = read_dimacs_file(rules_file_path)
        puzzle_clauses, puzzle_var_count = read_dimacs_file(puzzle_file_path)

        # Combine clauses
        combined_clauses = rules_clauses + puzzle_clauses

        solve_sudoku(combined_clauses)

## RUN using this in terminal

# I have not tested these scripts with other sizes of sudoku but it should work with the 5 examples provided.
# EX: python C:\github\sat_solver\sat_solver_21\Scripts\sat_solver_no_hueristics.py C:\github\sat_solver\sat_solver_21\sudoku_rules-9x9.cnf C:\github\sat_solver\sat_solver_21\examples\sudoku1.cnf
