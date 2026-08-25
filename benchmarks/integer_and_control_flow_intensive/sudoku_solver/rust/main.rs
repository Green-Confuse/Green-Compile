const N: usize = 9;

static mut GRID: [[i32; N]; N] = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
];

fn is_safe(row: usize, col: usize, num: i32) -> bool {
    unsafe {
        for i in 0..N {
            if GRID[row][i] == num || GRID[i][col] == num {
                return false;
            }
        }
        let start_row = row - row % 3;
        let start_col = col - col % 3;
        for r in 0..3 {
            for c in 0..3 {
                if GRID[start_row + r][start_col + c] == num {
                    return false;
                }
            }
        }
    }
    true
}

fn solve_sudoku() -> bool {
    let mut row: isize = -1;
    let mut col: isize = -1;
    let mut empty = false;
    unsafe {
        for r in 0..N {
            for c in 0..N {
                if GRID[r][c] == 0 {
                    row = r as isize;
                    col = c as isize;
                    empty = true;
                    break;
                }
            }
            if empty {
                break;
            }
        }
    }

    if !empty {
        return true;
    }

    for num in 1..=9 {
        if is_safe(row as usize, col as usize, num) {
            unsafe {
                GRID[row as usize][col as usize] = num;
            }
            if solve_sudoku() {
                return true;
            }
            unsafe {
                GRID[row as usize][col as usize] = 0;
            }
        }
    }
    false
}

fn main() {
    let _ = solve_sudoku();
}
