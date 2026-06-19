public class Main {
    static final int N = 256;
    static double[][] a = new double[N][N + 1];

    static void initMatrix() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                a[i][j] = ((i + 1) * (j + 1)) / (double)N;
            }
            a[i][N] = (double)(i + 1);
        }
    }

    static void gaussianElimination() {
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

    public static void main(String[] args) {
        initMatrix();
        gaussianElimination();
        double x0 = a[0][N];
        if (x0 == 0.0) {
            System.out.print("");
        }
    }
}
