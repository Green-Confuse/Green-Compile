#include <cstdint>

static uint32_t josephus(uint32_t n, uint32_t k) {
    uint32_t res = 0;
    for (uint32_t i = 1; i <= n; i++) {
        res = (res + k) % i;
    }
    return res + 1;
}

int main() {
    uint32_t n = 100000;
    uint32_t k = 3;
    volatile uint32_t survivor = josephus(n, k);
    (void)survivor;
    return 0;
}
