public class Main {
    static int josephus(int n, int k) {
        int res = 0;
        for (int i = 1; i <= n; i++) {
            res = (res + k) % i;
        }
        return res + 1;
    }

    public static void main(String[] args) {
        int n = 100000;
        int k = 3;
        int survivor = josephus(n, k);
    }
}
