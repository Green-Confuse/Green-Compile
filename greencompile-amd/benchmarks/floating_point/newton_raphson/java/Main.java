public class Main {
    static double newtonSqrt(double x) {
        double guess = x;
        for (int i = 0; i < 1000; i++) {
            guess = 0.5 * (guess + x / guess);
        }
        return guess;
    }

    public static void main(String[] args) {
        // [SCALED] 100K loop
        double sink = 0.0;
        for (int i = 1; i <= 100000; i++) {
            double x = (double) i * 0.123456789;
            sink += newtonSqrt(x);
        }
        if (sink == 0.0)
            System.out.print("");
    }
}
