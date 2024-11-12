import sys
import math as m 


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
    def varnum(r, c, v):
        return 100 * r + 10 * c + v

    # Add each given cell as a unit clause based on the clues in the puzzle
    for i, char in enumerate(sudoku_str):
        if char != '.':
            r = (i // n) + 1  # Row index (1-based)
            c = (i % n) + 1   # Column index (1-based)
            v = int(char)     # Value in the cell
            clauses.append([varnum(r, c, v)])  # Create unit clause

    # Prepare the DIMACS header and format the clauses
    num_vars = n * n * n  # Total number of possible variables
    num_clauses = len(clauses)  # Only the given clues are clauses
    dimacs_cnf = f"p cnf {num_vars} {num_clauses}\n"
    dimacs_cnf += "\n".join(" ".join(map(str, clause)) + " 0" for clause in clauses)
    
    return dimacs_cnf

def sudoku16_input_to_dimacs(sudoku_str):


    n = int(m.sqrt(len(sudoku_str)))  # Grid dimension (either 4, 9 or 16)
    hex_to_int = {str(i): i for i in range(1, 10)}
    hex_to_int.update({chr(c): i for i, c in enumerate(range(ord('A'), ord('G') + 1))})
    
    clauses = []

    # Helper to convert (row, col, value) to a unique variable in DIMACS format
    def varnum(r, c, v):
        return 17**2 * r + 17 * c + v

    # Add each given cell as a unit clause based on the clues in the puzzle
    for i, char in enumerate(sudoku_str):
        if char != '.':
            r = (i // n) + 1  # Row index (1-based)
            c = (i % n) + 1   # Column index (1-based)
            v = hex_to_int[char] + 1  # Convert hex character to integer and make 1-based
            clauses.append([varnum(r, c, v)])  # Create unit clause

    # Prepare the DIMACS header and format the clauses
    num_vars = 17**2 * 16 + 17 * 16 + 16  # Adjusted based on encoding scheme
    num_clauses = len(clauses)  # Only the given clues are clauses
    dimacs_cnf = f"p cnf {num_vars} {num_clauses}\n"
    dimacs_cnf += "\n".join(" ".join(map(str, clause)) + " 0" for clause in clauses)
    
    return dimacs_cnf




def merge_sudoku_dimacs_to_file(input_clues_str, constraints_file_path, output_file_path):
    """
    Merges the DIMACS CNF format strings of input clues and constraints,
    and writes the merged output to a new file.

    :param input_clues_str: DIMACS string representing the input clues only
    :param constraints_file_path: Path to the constraints DIMACS file
    :param output_file_path: Path where the combined DIMACS file will be written
    """

    
    # Read the constraints from the file
    with open(constraints_file_path, 'r') as file:
        constraints_str = file.read()
    
    # or read file 
    # sodku_test_path = sys.argv[1]
    # with open(sodku_test_path, 'r') as f:
    #     sodku_games = f.readlines()
    
    # # store all games in one file seperated by dash
    # with open(input_clues_str, 'w') as output_f:
    #     for game_index, sodku_game in sodku_games:
    #         sodku_game = sodku_game.strip()
    
    # Split header and clauses from both input clue and constraint strings
    clues_header, *clues_clauses = input_clues_str.strip().split("\n")
    constraints_header, *constraints_clauses = constraints_str.strip().split("\n")

    # Extract number of variables and clauses from the headers
    _, _, num_vars_clues, num_clauses_clues = clues_header.split()
    _, _, num_vars_constraints, num_clauses_constraints = constraints_header.split()

    # Calculate total number of variables and clauses
    num_vars = max(int(num_vars_clues), int(num_vars_constraints))
    num_clauses = int(num_clauses_clues) + int(num_clauses_constraints)

    # Create a new header with the updated number of clauses and variables
    combined_header = f"p cnf {num_vars} {num_clauses}"

    # Combine all clauses
    combined_clauses = "\n".join(clues_clauses + constraints_clauses)

    # Write the combined DIMACS content to the output file
    with open(output_file_path, 'w') as output_file:
        output_file.write(f"{combined_header}\n{combined_clauses}\n")
#       output_file.write("------\n")                                   # Separator between puzzles


sodoku_string2 = '...83A..C7.54..BC2...7.G..D..F...A..C8...6..3.5...9E..26.....C...3..AB.5D..47..87.C9....5....1F.ED1...3.....6.........17...6D.3A3G.D1...94.........B.....3...917.7A....4....8B.E9..6G..EB.7C..D...3.....69..E8...6.4..9...5D..G...2..C..G.F...ADD..GE.BA..325...'
input_clues_dimacs16 = sudoku16_input_to_dimacs(sodoku_string2)
# Example usage
sudoku_string = "....1..594...5.8...5.7........59..8..1.2.3....34........38...........6.7.729...1."  # Example 9x9 puzzle input
input_clues_dimacs = sudoku_input_to_dimacs(sudoku_string)

# Define paths for the constraint file and the output file
constraints_file_path = "/home/abdullah/KR/sat_solver_21/sudoku_rules/sudoku-rules-9x9.cnf"
output_file_path = "merged_sudoku.cnf"
merge_sudoku_dimacs_to_file(input_clues_dimacs, constraints_file_path, output_file_path)


# Define paths for the constraint file and the output file
constraints_file_path2 = "/home/abdullah/KR/sat_solver_21/sudoku_rules/sudoku-rules-16x16.cnf"
output_file_path2 = "merged_sudoku2.cnf"
# Merge and write to the output file
merge_sudoku_dimacs_to_file(input_clues_dimacs16, constraints_file_path2, output_file_path2)
print(f"Merged DIMACS output written to {output_file_path}")







#         # Convert the Sudoku string to DIMACS format
#         input_clues_dimacs = sudoku_input_to_dimacs(sodku_game, n)
#         merge_sudoku_dimacs_to_file(input_clues_dimacs, constraints_file_path, output_file_path)


        # merge all files into a 





# input_clues_dimacs = sudoku_input_to_dimacs(sudoku_string, n=9)

# # Define paths for the constraint file and the output file
# constraints_file_path = "/home/abdullah/KR/sat_solver_21/sudoku_rules/sudoku-rules-9x9.cnf"
# output_file_path = "merged_sudoku.cnf"

# # Merge and write to the output file
# merge_sudoku_dimacs_to_file(input_clues_dimacs, constraints_file_path, output_file_path)
# print(f"Merged DIMACS output written to {output_file_path}")
