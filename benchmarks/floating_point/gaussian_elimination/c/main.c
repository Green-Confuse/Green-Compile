#include <stdio.h>

#define N 256

static double a[N][N + 1];

static void init_matrix(void) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            a[i][j] = (double)((i + 1) * (j + 1)) / (double)(N);
        }
        a[i][N] = (double)(i + 1);
    }
}

static void gaussian_elimination(void) {
    for (int i = 0; i < N; i++) {
        double pivot = a[i][i];
        if (pivot == 0.0) {
            continue;
        }
        for (int j = i; j <= N; j++) {
            a[i][j] /= pivot;
        }
        for (int k = i + 1; k < N; k++) {
            double factor = a[k][i];
            for (int j = i; j <= N; j++) {
                a[k][j] -= factor * a[i][j];
            }
        }
    }
}

int main(void) {
    init_matrix();
    gaussian_elimination();
    volatile double x0 = a[0][N];
    (void)x0;
    return 0;
}
