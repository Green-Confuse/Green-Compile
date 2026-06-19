#include <stdio.h>
#include <stdbool.h>

#define N 9

static int grid[N][N] = {
    {5, 3, 0, 0, 7, 0, 0, 0, 0},
    {6, 0, 0, 1, 9, 5, 0, 0, 0},
    {0, 9, 8, 0, 0, 0, 0, 6, 0},
    {8, 0, 0, 0, 6, 0, 0, 0, 3},
    {4, 0, 0, 8, 0, 3, 0, 0, 1},
    {7, 0, 0, 0, 2, 0, 0, 0, 6},
    {0, 6, 0, 0, 0, 0, 2, 8, 0},
    {0, 0, 0, 4, 1, 9, 0, 0, 5},
    {0, 0, 0, 0, 8, 0, 0, 7, 9}
};

static bool is_safe(int row, int col, int num) {
    for (int i = 0; i < N; i++) {
        if (grid[row][i] == num || grid[i][col] == num) {
            return false;
        }
    }
    int start_row = row - row % 3;
    int start_col = col - col % 3;
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (grid[start_row + r][start_col + c] == num) {
                return false;
            }
        }
    }
    return true;
}

static bool solve_sudoku(void) {
    int row = -1;
    int col = -1;
    bool empty = false;
    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            if (grid[r][c] == 0) {
                row = r;
                col = c;
                empty = true;
                break;
            }
        }
        if (empty) {
            break;
        }
    }
    if (!empty) {
        return true;
    }

    for (int num = 1; num <= 9; num++) {
        if (is_safe(row, col, num)) {
            grid[row][col] = num;
            if (solve_sudoku()) {
                return true;
            }
            grid[row][col] = 0;
        }
    }
    return false;
}

int main(void) {
    (void)solve_sudoku();
    return 0;
}
