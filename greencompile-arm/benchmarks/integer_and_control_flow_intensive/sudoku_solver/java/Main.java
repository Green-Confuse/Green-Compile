public class Main {
    static final int N = 9;
    static int[][] grid = {
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

    static boolean isSafe(int row, int col, int num) {
        for (int i = 0; i < N; i++) {
            if (grid[row][i] == num || grid[i][col] == num) {
                return false;
            }
        }
        int startRow = row - row % 3;
        int startCol = col - col % 3;
        for (int r = 0; r < 3; r++) {
            for (int c = 0; c < 3; c++) {
                if (grid[startRow + r][startCol + c] == num) {
                    return false;
                }
            }
        }
        return true;
    }

    static boolean solveSudoku() {
        int row = -1;
        int col = -1;
        boolean empty = false;
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
            if (isSafe(row, col, num)) {
                grid[row][col] = num;
                if (solveSudoku()) {
                    return true;
                }
                grid[row][col] = 0;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        solveSudoku();
    }
}
