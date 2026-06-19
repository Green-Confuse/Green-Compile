#include <stdio.h>
#include <math.h>

static double newton_sqrt(double x) {
    double guess = x;
    for (int i = 0; i < 1000; i++) {
        guess = 0.5 * (guess + x / guess);
    }
    return guess;
}

int main(void) {
    /* [SCALED] Loop over 100000 seed values — ensures >500ms runtime */
    volatile double sink = 0.0;
    for (int i = 1; i <= 100000; i++) {
        double x = (double)i * 0.123456789;
        sink += newton_sqrt(x);
    }
    (void)sink;
    return 0;
}
