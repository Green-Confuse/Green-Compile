public class Main {
    private static final String A =
            "GCC and LLVM compilers optimize code; energy efficiency matters for modern CPUs.";
    private static final String B =
            "Modern CPU energy efficiency depends on compiler optimizations and runtime behavior.";

    private static int lcsLen(String a, String b) {
        int n = a.length();
        int m = b.length();
        int[] prev = new int[m + 1];
        int[] curr = new int[m + 1];

        for (int i = 1; i <= n; i++) {
            curr[0] = 0;
            for (int j = 1; j <= m; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) {
                    curr[j] = prev[j - 1] + 1;
                } else {
                    curr[j] = Math.max(prev[j], curr[j - 1]);
                }
            }
            int[] tmp = prev;
            prev = curr;
            curr = tmp;
        }
        return prev[m];
    }

    public static void main(String[] args) {
        int total = 0;
        for (int i = 0; i < 500; i++) {
            total += lcsLen(A, B);
        }
        if (total == 0) {
            System.out.print("");
        }
    }
}
