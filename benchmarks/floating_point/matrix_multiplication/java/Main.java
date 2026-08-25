public class Main {

    // Matrix multiplication method
    // a[m][n] × b[n][p] = result[m][p]
    public static double[][] mult(double[][] a, double[][] b) {

        // Edge case: empty matrix
        if (a.length == 0) {
            return new double[0][0];
        }

        // Invalid dimensions check
        if (a[0].length != b.length) {
            return null;
        }

        int m = a.length;        // rows of a
        int n = a[0].length;     // columns of a = rows of b
        int p = b[0].length;     // columns of b

        double[][] ans = new double[m][p];

        // Matrix multiplication logic
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < p; j++) {
                for (int k = 0; k < n; k++) {
                    ans[i][j] += a[i][k] * b[k][j];
                }
            }
        }

        return ans;
    }

    // Utility method to print a matrix
    public static void printMatrix(double[][] matrix) {
        if (matrix == null) {
            System.out.println("Invalid matrix dimensions!");
            return;
        }

        for (double[] row : matrix) {
            for (double val : row) {
                System.out.print(val + "\t");
            }
            System.out.println();
        }
    }

    // Main method to test the multiplication
    public static void main(String[] args) {

        double[][] a = {
                {1, 2, 3},
                {4, 5, 6}
        };

        double[][] b = {
                {7, 8},
                {9, 10},
                {11, 12}
        };

        double[][] result = mult(a, b);

        System.out.println("Resultant Matrix:");
        printMatrix(result);
    }
}
