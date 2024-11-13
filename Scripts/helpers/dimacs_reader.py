def read_dimacs_file(path):
    """load a DIMACS file and grab the clauses and var count."""
    clauses_list = []
    with open(path, 'r') as file:
        for line in file:
            # organizing 4 columns p cnf var_count clause_count
            if line.startswith('p cnf'):
                _, _, var_count, clause_count = line.split()
                var_count, clause_count = int(var_count), int(clause_count)
            else:
                clause = list(map(int, line.strip().split()))[:-1]
                clauses_list.append(clause)
    return clauses_list, var_count
