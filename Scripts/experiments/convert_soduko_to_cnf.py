import math as m

SUDOKU_RULES = '../../sudoku_rules/sudoku-rules-9x9.cnf'


def sudoku_string_to_cnf_clauses(sudoku):
    sudoku_cnf = sudoku_input_to_dimacs(sudoku)

    return merge_rules(sudoku_cnf, '../../sudoku_rules/sudoku-rules-9x9.cnf')


def sudoku_input_to_dimacs(sudoku_str):
    """
    Converts a Sudoku string with given clues into DIMACS CNF format,
    where only the clues are represented as unit clauses without additional constraints.
    
    :param sudoku_str: String representation of the Sudoku puzzle (e.g., "...3..4114..3...")
    :param n: Dimension of the Sudoku grid (4 for 4x4 or 9 for 9x9)
    :return: A string in DIMACS CNF format representing the puzzle
    """
    clauses = []
    n = int(m.sqrt(len(sudoku_str)))  # Grid dimension (either 4, 9 or 16)

    # Helper to convert (row, col, value) to a unique variable
    def varnum(row, column, value):
        return 100 * row + 10 * column + value

    # Add each given cell as a unit clause based on the clues in the puzzle
    for i, char in enumerate(sudoku_str):
        if char != '.':
            r = (i // n) + 1  # Row index (1-based)
            c = (i % n) + 1  # Column index (1-based)
            v = int(char)  # Value in the cell
            clauses.append([varnum(r, c, v)])  # Create unit clause

    return clauses


def merge_rules(input_clues_str, constraints_file_path):
    """
    Merges the DIMACS CNF format strings of input clues and constraints,
    and writes the merged output to a new file.

    :param input_clues_str: DIMACS string representing the input clues only
    :param constraints_file_path: Path to the constraints DIMACS file
    :param output_file_path: Path where the combined DIMACS file will be written
    """

    # Read the constraints from the file
    with open(constraints_file_path, 'r') as file:
        rules = file.read().splitlines()

        header = rules[0]
        _, _, total_variables, _ = header.split()
        rules.remove(header)

        rule_clauses = [rule.replace(' 0', '') for rule in rules]
        rules_as_int = [
            list(map(int, clause.strip().replace(' 0', '').split()))[:-1]
            for clause in rule_clauses
        ]

        return (rules_as_int + input_clues_str), int(total_variables)
