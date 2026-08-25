#include <stdio.h>
#include <stdbool.h>

#define N 8

static int board[N][N];
static int dx[8] = {2, 1, -1, -2, -2, -1, 1, 2};
static int dy[8] = {1, 2, 2, 1, -1, -2, -2, -1};

static bool is_valid(int x, int y) {
    return x >= 0 && x < N && y >= 0 && y < N && board[y][x] == -1;
}

static int degree(int x, int y) {
    int count = 0;
    for (int i = 0; i < 8; i++) {
        int nx = x + dx[i];
        int ny = y + dy[i];
        if (is_valid(nx, ny)) {
            count++;
        }
    }
    return count;
}

static bool solve(int x, int y, int move) {
    if (move == N * N) {
        return true;
    }

    int cand_x[8];
    int cand_y[8];
    int cand_deg[8];
    int count = 0;

    for (int i = 0; i < 8; i++) {
        int nx = x + dx[i];
        int ny = y + dy[i];
        if (is_valid(nx, ny)) {
            cand_x[count] = nx;
            cand_y[count] = ny;
            cand_deg[count] = degree(nx, ny);
            count++;
        }
    }

    for (int i = 0; i < count; i++) {
        int best = i;
        for (int j = i + 1; j < count; j++) {
            if (cand_deg[j] < cand_deg[best]) {
                best = j;
            }
        }
        int tx = cand_x[i];
        int ty = cand_y[i];
        int td = cand_deg[i];
        cand_x[i] = cand_x[best];
        cand_y[i] = cand_y[best];
        cand_deg[i] = cand_deg[best];
        cand_x[best] = tx;
        cand_y[best] = ty;
        cand_deg[best] = td;

        int nx = cand_x[i];
        int ny = cand_y[i];
        board[ny][nx] = move;
        if (solve(nx, ny, move + 1)) {
            return true;
        }
        board[ny][nx] = -1;
    }

    return false;
}

int main(void) {
    for (int y = 0; y < N; y++) {
        for (int x = 0; x < N; x++) {
            board[y][x] = -1;
        }
    }
    board[0][0] = 0;
    (void)solve(0, 0, 1);
    return 0;
}
