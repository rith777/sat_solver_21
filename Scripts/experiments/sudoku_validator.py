import math
from collections import Counter


def is_valid_sudoku(matrix):
    return _are_all_rows_valid(matrix) and _are_all_columns_valid(matrix) and _are_all_sub_grids_valid(matrix)


def _are_all_rows_valid(matrix):
    for row in matrix:
        if not _are_all_values_unique(row):
            return False
    return True


def _are_all_columns_valid(matrix):
    number_of_rows = len(matrix)
    for col in range(number_of_rows):
        if not _are_all_values_unique([matrix[row][col] for row in range(number_of_rows)]):
            return False
    return True


def _are_all_sub_grids_valid(matrix):
    number_of_rows = len(matrix)
    sub_grid_size = int(math.sqrt(number_of_rows))

    for box_row in range(0, number_of_rows, sub_grid_size):
        for box_col in range(0, number_of_rows, sub_grid_size):
            subgrid = [matrix[row][column]
                       for row in range(box_row, box_row + sub_grid_size)
                       for column in range(box_col, box_col + sub_grid_size)]
            if not _are_all_values_unique(subgrid):
                return False
    return True


def _are_all_values_unique(unit):
    count = Counter(unit).values()

    return all(value == 1 for value in count)
