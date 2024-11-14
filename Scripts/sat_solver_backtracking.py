import sys

from helpers.dimacs_reader import read_dimacs_file
from helpers.sat_outcome_converter import from_dict_to_cnf, from_dict_to_matrix, pretty_matrix
def unit_propagate(clauses, assign):
    """Simplify clauses with unit propagation."""
    has_changes = True
    unit_count = 0  # Count of unit clauses processed

    while has_changes:
        has_changes = False
        unit_clauses = find_all_unit_literals_in(clauses)

        print(f"Unit propagation round: {len(unit_clauses)} unit clauses found.")

        for unit in unit_clauses:
            assign[abs(unit)] = unit > 0  # Set the variable's value
            clauses = [clause for clause in clauses if unit not in clause]

            # Remove negation of unit clause
            for clause in clauses:
                if -unit in clause:
                    clause.remove(-unit)
            has_changes = True
            unit_count += 1

    print(f"Total unit clauses processed: {unit_count}")
    return clauses, assign



def find_all_unit_literals_in(clauses):
    return [clause[0] for clause in clauses if len(clause) == 1]

def eliminate_pure_literal(clauses, assign):
    """assign values to pure literals"""
    literals = [literal for clause in clauses for literal in clause]

    # identifying pure literals
    pure_literals = [literal for literal in set(literals) if -literal not in literals]

    print(f"Pure literal elimination round: {len(pure_literals)} pure literals found.")

    for literal in pure_literals:
        assign[abs(literal)] = literal > 0  # Set true or false for positive or negative pure lit
        clauses = [clause for clause in clauses if literal not in clause]

    print(f"Total pure literals eliminated: {len(pure_literals)}")
    return clauses, assign

import random

def dpll_algorithm(clauses, assign, decision_stack, attempt_count=0, backtrack_count=0):
    """DPLL algorithm with backtracking."""
    # Simplify clauses with unit propagation and pure literal elimination
    clauses, assign = unit_propagate(clauses, assign)
    clauses, assign = eliminate_pure_literal(clauses, assign)

    # Debugging: Show the clauses and assignment after simplification
    print(f"Clauses after simplification: {len(clauses)} remaining")
    print(f"Assignment count after simplification: {len(assign)}")

    # Base case: If all clauses are satisfied, return SATISFIABLE
    if not clauses:  # All clauses satisfied
        print("All clauses satisfied. Puzzle solved.")
        if is_valid_assignment(assign):
            return True, assign
        else:
            print("Assignment is invalid, backtracking.")
            return False, {}

    # If any clause is empty, we found an unsatisfiable clause
    if any(len(clause) == 0 for clause in clauses):  # Unsatisfiable clause
        print("Unsatisfiable clause found. Backtracking.")
        return False, {}

    # Find the unassigned literals
    unassigned = find_unassigned_literals(assign, clauses)
    if not unassigned:  # If no unassigned literals left, we're stuck
        print("No unassigned literals left to process.")
        return False, {}

    # Randomly select a variable to assign
    selected_var = random.choice(unassigned)  # Randomly choose from unassigned literals
    decision_stack.append(selected_var)  # Track the decision for backtracking

    # Try assigning True to the selected variable
    updated_assign = assign.copy()
    updated_assign[selected_var] = True
    attempt_count += 1  # Increase the attempt count

    print(f"Assignment attempt #{attempt_count}: {selected_var} = True")
    new_clauses = [clause for clause in clauses if selected_var not in clause]
    sat, result = dpll_algorithm(new_clauses, updated_assign, decision_stack, attempt_count, backtrack_count)

    if not sat:
        # If True didn't work, backtrack and try False
        backtrack_count += 1  # Increase the backtracking count
        print(f"Backtracking #{backtrack_count}: Trying {selected_var} = False")
        updated_assign[selected_var] = False
        new_clauses = [clause for clause in clauses if -selected_var not in clause]
        sat, result = dpll_algorithm(new_clauses, updated_assign, decision_stack, attempt_count, backtrack_count)

    # Debugging: Show backtracking count and the result of attempts
    print(f"Total assignment attempts: {attempt_count}")
    print(f"Total backtracking events: {backtrack_count}")

    # If we still didn't find a solution, backtrack to the previous decision
    if not sat:
        print(f"Backtracking from {selected_var} to previous decision point.")
        decision_stack.pop()  # Pop the current decision as we backtrack

    return sat, result


def is_valid_assignment(assign):
    """Check if all variables have been assigned a valid value (no 0s)."""
    return all(value is not None for value in assign.values())





def find_unassigned_literals(assign, clauses):
    unassigned = [abs(literal) for clause in clauses for literal in clause if abs(literal) not in assign]
    return unassigned


def save_output(path, assign, satisfiable):
    """Write result to output file (ex filename.out)."""
    output_file = path + '.out'
    sudoku_path = path.replace(".cnf", ".txt")

    # Debugging: Check the assignment dictionary
    missing_vars = [var for var in range(1, 730) if var not in assign or assign[var] is None]
    if missing_vars:
        print(f"ERROR: The following variables are missing assignments: {missing_vars}")
    else:
        print("All variables assigned.")

    if satisfiable:
        with open(output_file, 'w') as output:
            result = from_dict_to_cnf(assign)
            print(f"Writing CNF result: {result}")  # Debugging print
            output.write(" 0 \n".join(result))

        with open(sudoku_path, mode='w') as sudoku:
            matrix_result = pretty_matrix(from_dict_to_matrix(assign))
            print(f"Writing Sudoku matrix result: {matrix_result}")  # Debugging print
            sudoku.write(matrix_result)

    else:
        with open(output_file, 'w') as output:
            output.write("UNSATISFIABLE\n")
        with open(sudoku_path, mode='w') as sudoku:
            sudoku.write("UNSATISFIABLE\n")


def solve_sudoku(clauses):
    assign = {}
    decision_stack = []  # Initialize the decision stack
    is_satisfiable, final_assignment = dpll_algorithm(clauses, assign, decision_stack)

    # Save the result to an output file based on the puzzle path
    save_output(puzzle_file_path, final_assignment, is_satisfiable)

    print(f"Final result: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
    print(f"Final assignment size (if SATISFIABLE): {len(final_assignment)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sat_solver_backtracking.py <rulesfilepath> <puzzlefilepath>")
    else:
        rules_file_path = sys.argv[1]
        puzzle_file_path = sys.argv[2]

        # Load rules and puzzle clauses
        rules_clauses, rules_var_count = read_dimacs_file(rules_file_path)
        puzzle_clauses, puzzle_var_count = read_dimacs_file(puzzle_file_path)

        # Combine clauses
        combined_clauses = rules_clauses + puzzle_clauses

        solve_sudoku(combined_clauses)
