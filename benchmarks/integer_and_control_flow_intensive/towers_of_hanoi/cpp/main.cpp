#include <iostream>

void hanoi(int n, int from, int to, int aux) {
    if (n == 0) return;
    hanoi(n - 1, from, aux, to);
    hanoi(n - 1, aux, to, from);
}

int main() {
    int N = 27;
    hanoi(N, 1, 3, 2);
    return 0;
}
