# Sat solver

The following SAT solver algorithms have been implemented:

- Recursive `DPLL`
- `CDCL` with 2 different heuristics(CHB and VSIDS).

## Running the sat solver:

1. Run the command `chmod +x SAT` to ensure the SAT script is executable.
2. Execute the SAT script: `./SAT -Sn sudoku.cnf `

`n` represents the algorithm to be performed. Replace `n` with one of the following options:

1. Basic DPLL sat solver
2. CDCL SAT solver using CHB heuristics
3. CDCL SAT solver using VSIDS heuristics

Once the script is executed, the statistics and a sudoku matrix will be printed in the console.

## Experimentation

### Running experiments

To facilitate experimentation, a script to run multiple SAT executions asynchronously was added.
The script can be found on `experiment_runner.py`. This script will solve all sudokus available in a given dataset using
both DPLL and CDCL (CHB and VISIDs).

To run experiments, follow the steps bellow:

1. Change the constant `SUDOKU_DATASET_FILE_PATH` in `experiment_runner.py` to add the desired dataset.
2. Run script on  `experiment_runner.py`

A file `experiment_result.csv` will be created as outcome of the experimentation script. This file contains statistics
for all SAT
solvers implemented in this repository.

### Sudoku strings

Experimentation consists on running a file with several sudoku strings. A sudoku string looks like
this: `2.48........7.5....13.....9..7.......26....3.3...26.4...9..845.87.....16....6.2..`.
In this case, each `.` represents a unknown number, to be solved by the SAT solver. Any existing number represents a
clue.

### Quality evaluation

Sudoku is used as input to test and compare SAT solvers. Having the SAT solver to return a positive outcome (
eg. `SATISFIABLE`)
is not enough to guarantee the sudoku was properly solved.

For each execution of a specific SAT solver during experimentation, a quality step takes place. At this step,
the solution returned by the SAT solver is tested against the sudoku rules (see `sudoku_validator.py`) .
If the SAT solver returns a positive response (eg. `SATISFIABLE`) and an invalid solution, then the SAT solver itself is
considered defective.

*Note:* This only works for 9x9 sudokus.

### Collected metrics

Whenever each SAT solver algorithm runs, individual metrics are collected. Those metrics are later stored in a `.csv`
file as described in [Running experiments](#running-experiments).

To make it easier to identify what metric refers to each algorith, prefixes are added to each column in the final `.csv`
file. The following prefixes were added:

- `CDCL` with `VISIDS` heuristics: `VSIDS_`
- `CDCL` with `CHB` heuristics: `CHB_`
- DPLL with random heuristics: `basic_DPLL_`
- Sudoku string: `unsolved_sudoku`

The original unsolved sudoku string is also collected. This makes it easy to identify which sudoku caused a specific
outcome. This can be useful for both data analysis and for bug analysis.

#### DPLL

- **backtrack**: Indicates how many times the algorithm hit a dead end and it has to try again, with a different
  decision
- **clause simplification**: Counts how many times clauses were simplified. Clause simplification reduces the clause
  sice and remove redundancies.
- **conflicts**: It counts how many inconsistencies were found.
- **decisions**: Counts the explicit choices made by the SAT solver (eg.: explicitly assign *True* or *False* to literal
  111).
- **Implications**: Counts the amount of implications. It indicates how many decisions based on logic were made. It
  differs from decision, because a decision is a explicit choice, while implication is a deduction
- **recursions**: Total amount of recursions performed while running the algorithm. Deeper recursion can indicate
  inefficiency or complex problem structure.

#### CDCL

- **backjumps**: Counts how many back jumps were performed. Backjumps (equivalent to backtrack) took place
- **conflicts**: It counts how many inconsistencies were found.
- **decisions**: Counts the explicit choices made by the SAT solver (eg.: explicitly assign *True* or *False* to literal
  111).
- **Implications**: Counts the amount of implications. It indicates how many decisions based on logic were made. It
  differs from decision, because a decision is a explicit choice, while implication is a deduction
- **learned clauses**: Indicates how many times the solver learned new clauses when solving conflicts.

#### Unsolved sudoku

Metrics are also collected from the initial [sudoku string](#sudoku-strings).

Bellow are the collected metrics:

- **Number of clues**: number of know numbers (clues)
- **Number unknown positions**: Counts the amount of `.` on the sudoku string
- **Total of characters**: Counts the amount of characters in the sudoku string (including numbers and `.`). Used for
  validation purposes. Number of clues + Number of unknown position should be equal to the total of characters.

#### Other collected data

This section describe other data collected for all SAT solver algorithms implemented in this codebase.

- **is_satisfied**: Boolean flag. False means there is no solution for the given sudoku string (`UNSAT`). True means a
  solution was found (`SAT`).
- **is_solution_valid**: Boolean flag. It runs a quality check step to validate the final solution
  see [quality evaluation](#quality-evaluation)
