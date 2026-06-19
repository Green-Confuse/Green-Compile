const N: usize = 8;

static mut BOARD: [[i32; N]; N] = [[-1; N]; N];
static DX: [i32; 8] = [2, 1, -1, -2, -2, -1, 1, 2];
static DY: [i32; 8] = [1, 2, 2, 1, -1, -2, -2, -1];

fn is_valid(x: i32, y: i32) -> bool {
    if x < 0 || y < 0 || x >= N as i32 || y >= N as i32 {
        return false;
    }
    unsafe { BOARD[y as usize][x as usize] == -1 }
}

fn degree(x: i32, y: i32) -> i32 {
    let mut count = 0;
    for i in 0..8 {
        let nx = x + DX[i];
        let ny = y + DY[i];
        if is_valid(nx, ny) {
            count += 1;
        }
    }
    count
}

fn solve(x: i32, y: i32, mv: i32) -> bool {
    if mv == (N * N) as i32 {
        return true;
    }

    let mut cand_x = [0i32; 8];
    let mut cand_y = [0i32; 8];
    let mut cand_deg = [0i32; 8];
    let mut count = 0;

    for i in 0..8 {
        let nx = x + DX[i];
        let ny = y + DY[i];
        if is_valid(nx, ny) {
            cand_x[count] = nx;
            cand_y[count] = ny;
            cand_deg[count] = degree(nx, ny);
            count += 1;
        }
    }

    for i in 0..count {
        let mut best = i;
        for j in (i + 1)..count {
            if cand_deg[j] < cand_deg[best] {
                best = j;
            }
        }
        cand_x.swap(i, best);
        cand_y.swap(i, best);
        cand_deg.swap(i, best);

        let nx = cand_x[i];
        let ny = cand_y[i];
        unsafe {
            BOARD[ny as usize][nx as usize] = mv;
        }
        if solve(nx, ny, mv + 1) {
            return true;
        }
        unsafe {
            BOARD[ny as usize][nx as usize] = -1;
        }
    }

    false
}

fn main() {
    unsafe {
        for y in 0..N {
            for x in 0..N {
                BOARD[y][x] = -1;
            }
        }
        BOARD[0][0] = 0;
    }
    let _ = solve(0, 0, 1);
}
