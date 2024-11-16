# Sat solver

This repository contains 2 different SAT solvers, a basic DPLL and a CDCL.

## Running the sat solver:

1. Run the command `chmod +x SAT` to ensure the SAT script is executable.
2. Execute the SAT script: `./SAT -Sn sudoku.cnf `

`n` represents the algorithm to be performed. Replace `n` with one of the following options:

1. Basic DPLL sat solver
2. CDCL SAT solver using CHB heuristics
3. CDCL SAT solver using VSIDS heuristics

Once the script is executed, the statistics and a sudoku matrix will be printed in the console.

## running experiments

To facilitate experimentation, a script to run multiple SAT executions asynchronously was added.
The script can be found on `experiment_runner.py`. This script will solve all sudokus available in a given dataset using both DPLL and CDCL (CHB and VISIDs). 

To run experiments, follow the steps bellow:

1. Run `pip install -r requirements.txt` to install the required dependencies
2. Change the constant `SUDOKU_DATASET_FILE_PATH` in `experiment_runner.py` to add the desired dataset.
3. Run script on  `experiment_runner.py`

A file `output.csv` will be created as outcome of the experimentation script. This file contains statistics for all SAT
solvers implemented in this repository. 