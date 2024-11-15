import sys


from helpers.dimacs_reader import read_dimacs_file
from helpers.sat_outcome_converter import from_dict_to_cnf, from_dict_to_matrix, pretty_matrix




def simplify_clauses(clauses, literal):
    """
    Simplifies the clause list by applying a literal's assignment.
    """
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue  # Clause is satisfied
        new_clause = [lit for lit in clause if lit != -literal]
        new_clauses.append(new_clause)
    return new_clauses


def find_pure_literals(clauses):
    """
    Finds pure literals in the given clauses.
    """
    counts = {}
    for clause in clauses:
        for literal in clause:
            counts[literal] = counts.get(literal, 0) + 1
    pure_literals = [lit for lit in counts if -lit not in counts]
    return pure_literals
def dpll(clauses, assignment={}):
    """
    Basic DPLL Algorithm for SAT solving.
    """
    # Base case: All clauses are satisfied
    if not clauses:
        return True, assignment

    # Base case: A clause is unsatisfiable (empty clause exists)
    if any(len(clause) == 0 for clause in clauses):
        return False, {}

    # Unit propagation: Assign values based on unit clauses
    for clause in clauses:
        if len(clause) == 1:  # Unit clause found
            unit = clause[0]
            value = unit > 0
            assignment[abs(unit)] = value
            # Simplify clauses with the unit literal
            clauses = simplify_clauses(clauses, unit)
            return dpll(clauses, assignment)

    # Pure literal elimination: Assign values to pure literals
    pure_literals = find_pure_literals(clauses)
    if pure_literals:
        for pure in pure_literals:
            assignment[abs(pure)] = pure > 0
            clauses = simplify_clauses(clauses, pure)
        return dpll(clauses, assignment)

    # Choose a variable to assign (simple heuristic: first unassigned variable)
    variable = None  # Initialize variable
    for clause in clauses:
        for literal in clause:
            if abs(literal) not in assignment:
                variable = abs(literal)
                break
        if variable is not None:
            break

    # If no unassigned variable is found, return
    if variable is None:
        return False, assignment  # No variable to assign

    # Try assigning True to the variable
    new_assignment = assignment.copy()
    new_assignment[variable] = True
    result, final_assignment = dpll(simplify_clauses(clauses, variable), new_assignment)
    if result:
        return True, final_assignment

    # If assigning True fails, try assigning False
    new_assignment[variable] = False
    return dpll(simplify_clauses(clauses, -variable), new_assignment)
def save_output(filepath, satisfiable, assignment):
    """
    Saves the SAT solving results to an output file and a readable Sudoku format.
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
        sudoku_string = pretty_matrix(sudoku_matrix)    # Format the matrix into a string

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

    # Solve the SAT problem
    satisfiable, assignment = dpll(combined_clauses)

    # Save the results and display them
    save_output(puzzle_file_path, satisfiable, assignment, grid_size=9)
    print(f"Result: {'SATISFIABLE' if satisfiable else 'UNSATISFIABLE'}")
    if satisfiable:
        print(f"Satisfying Assignment Size: {len(assignment)}")