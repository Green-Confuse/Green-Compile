public class Main {

    static void hanoi(int n, int from, int to, int aux) {
        if (n == 0) return;
        hanoi(n - 1, from, aux, to);
        hanoi(n - 1, aux, to, from);
    }

    public static void main(String[] args) {
        int N = 27;
        hanoi(N, 1, 3, 2);
    }
}
