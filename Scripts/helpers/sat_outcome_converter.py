def from_list_to_matrix(data: list):
    sudoku = _empty_matrix()

    for value in data:
        if value > 0:
            row, column, value = list(str(value).strip())

            row_index, column_index = int(row) - 1, int(column) - 1

            if sudoku[row_index][column_index] == 0:
                sudoku[row_index][column_index] = int(value)

    return sudoku


def from_dict_to_matrix(data: dict):
    sudoku = _empty_matrix()

    for key, value in data.items():
        if value:
            row, column, value = list(str(key).strip())
            sudoku[int(row) - 1][int(column) - 1] = int(value)

    return sudoku


def from_dict_to_cnf(data: dict):
    return [str(key) if value else str(-key) for key, value in data.items()]


def _empty_matrix():
    return [[0 for _ in range(9)] for _ in range(9)]


def pretty_matrix(matrix):
    return '\n'.join(['\t'.join([str(cell) for cell in row]) for row in matrix])
