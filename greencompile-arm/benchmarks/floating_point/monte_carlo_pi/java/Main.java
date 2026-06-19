public class Main {
    static long lcgNext(long state) {
        return state * 6364136223846793005L + 1L;
    }

    public static void main(String[] args) {
        final long samples = 500000000L;
        long inside = 0;
        long state = 1L;
        final double scale = 1.0 / 9007199254740992.0;

        for (long i = 0; i < samples; i++) {
            state = lcgNext(state);
            long r1 = state;
            state = lcgNext(state);
            long r2 = state;
            double x = (double)(r1 >>> 11) * scale;
            double y = (double)(r2 >>> 11) * scale;
            double d = x * x + y * y;
            if (d <= 1.0) {
                inside++;
            }
        }

        double pi = 4.0 * (double)inside / (double)samples;
        if (pi == 0.0) {
            System.out.print("");
        }
    }
}
