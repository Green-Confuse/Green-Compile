#include <stdio.h>

static double f(double x) {
    return 4.0 / (1.0 + x * x);
}

static double simpson(double a, double b, int n) {
    if (n % 2 != 0) {
        n++;
    }
    double h = (b - a) / n;
    double sum = f(a) + f(b);
    for (int i = 1; i < n; i++) {
        double x = a + h * i;
        if (i % 2 == 0) {
            sum += 2.0 * f(x);
        } else {
            sum += 4.0 * f(x);
        }
    }
    return sum * h / 3.0;
}

static double trapezoidal(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = 0.5 * (f(a) + f(b));
    for (int i = 1; i < n; i++) {
        double x = a + h * i;
        sum += f(x);
    }
    return sum * h;
}

int main(void) {
    double a = 0.0;
    double b = 1.0;
    int n = 50000000;
    volatile double s = simpson(a, b, n);
    volatile double t = trapezoidal(a, b, n);
    (void)s;
    (void)t;
    return 0;
}
