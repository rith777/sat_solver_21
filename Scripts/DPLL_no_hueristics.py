import sys

def load_my_file(path):
    """load a DIMACS file and grab the clauses and var count."""
    clauses_list = []
    with open(path, 'r') as f:
        for line in f:
            #organizing 4 columns p cnf var_count clause_count
            if line.startswith('p cnf'):
                _, _, var_count, clause_count = line.split()
                var_count, clause_count = int(var_count), int(clause_count)
            else:
                clause = list(map(int, line.strip().split()))[:-1]
                clauses_list.append(clause) #add clause to list of clauses
    return clauses_list, var_count #return clause and var count

def unit_propagate(clauses, assign):
    """simplify clauses with unit propagation."""
    has_changes = True
    while has_changes: #run until changes are found in list of clauses.
        has_changes = False
        unit_clauses = [] #hold clauses with one literal

        #find unit clauses
        for c in clauses:
            if len(c) == 1:
                unit_clauses.append(c[0]) #adds all clauses with one var (or unit clauses)

        #processing unit clauses
        for unit in unit_clauses:
            assign[abs(unit)] = unit > 0  #setting var in unit clause to true or false

            new_clauses = [] #post unit clauses collection of clauses
            for c in clauses:
                if unit not in c: #add clauses disatisfying with unit clause
                    new_clauses.append(c)
            clauses = new_clauses

            # Remove negation of unit clauses too (ex: removing p and not(p) if p is a literal)
            for clause in clauses:
                if -unit in clause: #if negated unit clause in clause you can remove it from the clause
                    clause.remove(-unit)
            has_changes = True # revert boolean to say change has been made.
    return clauses, assign #return assignment and updated clauses without literal

def eliminate_pure_lit(clauses, assign):
    """assign values to pure literals"""
    all_lits = []
    for c in clauses:
        for lit in c:
            all_lits.append(lit) #all literals from all clauses

    # identifying pure lits and assigning truth valeus
    for lit in set(all_lits):
        if -lit not in all_lits:  # if negation absent it is pure (ex if p then not(p) should not be in lit for p to be pure)
            assign[abs(lit)] = lit > 0  # Set true or false for positive or negative pure lit
            # if it's a positive pure literal (ex p), we can assign it true
            # If it's a negative pure literal (ex, ¬p), we can assign its (p) to False

            new_clauses = []
            for c in clauses: #basically discards all clauses with the pure literal returns updated list of clauses
                if lit not in c:
                    new_clauses.append(c)
            clauses = new_clauses
    return clauses, assign

def dpll_algorithm(clauses, assign):
    """DPLL algorithm"""

    # do unit propagation and pure lit elimination
    clauses, assign = unit_propagate(clauses, assign)
    clauses, assign = eliminate_pure_lit(clauses, assign)


    if not clauses:  # All clauses satisfied so return true (solution found!!!)
        return True, assign
    if any(len(c) == 0 for c in clauses):  # Found an unsatisfiable clause
        return False, {}


    unassigned_vars = [] #makes sure all vars are only picked once
    for c in clauses: #check all clauses
        for lit in c: #check all literals
            if abs(lit) not in assign: #check if the absolute value of the literal is not in the assigned variables
                unassigned_vars.append(abs(lit)) #add abs value of var to unassigned_vars
    if not unassigned_vars:  # if empty then it should be unsatisfiable
        return False, {}

    selected_var = unassigned_vars[0]  # take the first one

    # Try assigning True to the selected variable
    updated_assign = assign.copy()
    updated_assign[selected_var] = True

    #recursive call with updated assignment of var and filter out clauses that selected var satisfies
    sat, result = dpll_algorithm([c for c in clauses if selected_var not in c],
                                        updated_assign)
    if sat: #if satisfiable return true
        return True, result

    # update assignment var as false and try the same recursive call
    updated_assign[selected_var] = False
    sat, result = dpll_algorithm([c for c in clauses if -selected_var not in c],
                                        updated_assign)
    return sat, result

def save_my_output(path, assign, satisfiable):
    """Write result to output file (ex filename.out)."""
    output_file = path + '.out'
    with open(output_file, 'w') as output:
        if satisfiable:
            #write the truth assignment for each variable
            for var in range(1, 730): #for all 729 variables that are being outputted
                if var in assign:
                    output.write(f"{var if assign[var] else -var} 0\n")
        else:
            output.write("")  # Write empty file for unsatisfiable
def main_flow():
    if len(sys.argv) != 3:
        print("Usage: python DPLL_no_heuristics.py <rulesfilepath> <puzzlefilepath>")
        return

    rules_file_path = sys.argv[1]
    puzzle_file_path = sys.argv[2]

    # Load rules and puzzle clauses
    rules_clauses, rules_var_count = load_my_file(rules_file_path)
    puzzle_clauses, puzzle_var_count = load_my_file(puzzle_file_path)

    # Combine clauses
    combined_clauses = rules_clauses + puzzle_clauses

    assign = {}
    is_satisfiable, final_assignment = dpll_algorithm(combined_clauses, assign)

    # Save the result to an output file based on the puzzle path
    save_my_output(puzzle_file_path, final_assignment, is_satisfiable)

    if is_satisfiable:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main_flow()

## RUN using this in terminal
# EX: python C:\github\sat_solver\sat_solver_21\Scripts\DPLL_no_hueristics.py C:\github\sat_solver\sat_solver_21\examples\sudoku1.cnf