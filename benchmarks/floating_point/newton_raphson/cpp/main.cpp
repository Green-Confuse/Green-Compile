#include <cmath>

static double newton_sqrt(double x) {
    double guess = x;
    for (int i = 0; i < 1000; i++) {
        guess = 0.5 * (guess + x / guess);
    }
    return guess;
}

int main() {
    double x = 12345.6789;
    volatile double root = newton_sqrt(x);
    (void)root;
    return 0;
}
