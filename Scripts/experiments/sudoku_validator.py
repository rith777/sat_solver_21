def is_valid_sudoku(matrix):
    return _are_all_rows_valid(matrix) and _are_all_columns_valid(matrix) and _are_all_3_by_3_grid_valid(matrix)


def _are_all_rows_valid(matrix):
    for row in matrix:
        if not _are_all_values_unique(row):
            return False
    return True


def _are_all_columns_valid(matrix):
    for col in range(9):
        if not _are_all_values_unique([matrix[row][col] for row in range(9)]):
            return False
    return True


def _are_all_3_by_3_grid_valid(matrix):
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            subgrid = [matrix[row][column]
                       for row in range(box_row, box_row + 3)
                       for column in range(box_col, box_col + 3)]
            if not _are_all_values_unique(subgrid):
                return False
    return True


def _are_all_values_unique(unit):
    unit = [num for num in unit if num != 0]
    return len(unit) == len(set(unit))
