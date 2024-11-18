import math as m

from Scripts.helpers.dimacs_reader import read_dimacs_file

SUDOKU_RULES = '../../sudoku_rules/sudoku-rules-9x9.cnf'


def sudoku_string_to_cnf_clauses(sudoku):
    sudoku_cnf = sudoku_input_to_dimacs(sudoku)

    return merge_rules(sudoku_cnf, '../../sudoku_rules/sudoku-rules-9x9.cnf')


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


def merge_rules(clues, constraints_file_path):
    rules, var_count = read_dimacs_file(constraints_file_path)

    return (clues + rules), var_count
