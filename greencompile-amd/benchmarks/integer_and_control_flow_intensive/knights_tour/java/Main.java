public class Main {
    static final int N = 8;
    static int[][] board = new int[N][N];
    static int[] dx = {2, 1, -1, -2, -2, -1, 1, 2};
    static int[] dy = {1, 2, 2, 1, -1, -2, -2, -1};

    static boolean isValid(int x, int y) {
        return x >= 0 && x < N && y >= 0 && y < N && board[y][x] == -1;
    }

    static int degree(int x, int y) {
        int count = 0;
        for (int i = 0; i < 8; i++) {
            int nx = x + dx[i];
            int ny = y + dy[i];
            if (isValid(nx, ny)) {
                count++;
            }
        }
        return count;
    }

    static boolean solve(int x, int y, int move) {
        if (move == N * N) {
            return true;
        }

        int[] candX = new int[8];
        int[] candY = new int[8];
        int[] candDeg = new int[8];
        int count = 0;

        for (int i = 0; i < 8; i++) {
            int nx = x + dx[i];
            int ny = y + dy[i];
            if (isValid(nx, ny)) {
                candX[count] = nx;
                candY[count] = ny;
                candDeg[count] = degree(nx, ny);
                count++;
            }
        }

        for (int i = 0; i < count; i++) {
            int best = i;
            for (int j = i + 1; j < count; j++) {
                if (candDeg[j] < candDeg[best]) {
                    best = j;
                }
            }
            int tx = candX[i];
            int ty = candY[i];
            int td = candDeg[i];
            candX[i] = candX[best];
            candY[i] = candY[best];
            candDeg[i] = candDeg[best];
            candX[best] = tx;
            candY[best] = ty;
            candDeg[best] = td;

            int nx = candX[i];
            int ny = candY[i];
            board[ny][nx] = move;
            if (solve(nx, ny, move + 1)) {
                return true;
            }
            board[ny][nx] = -1;
        }

        return false;
    }

    public static void main(String[] args) {
        for (int y = 0; y < N; y++) {
            for (int x = 0; x < N; x++) {
                board[y][x] = -1;
            }
        }
        board[0][0] = 0;
        solve(0, 0, 1);
    }
}
