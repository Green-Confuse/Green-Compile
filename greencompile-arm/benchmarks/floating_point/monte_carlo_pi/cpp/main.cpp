#include <cstdint>

static uint64_t lcg_next(uint64_t &state) {
    state = state * 6364136223846793005ULL + 1ULL;
    return state;
}

int main() {
    const uint64_t samples = 500000000ULL;
    uint64_t inside = 0;
    uint64_t state = 1ULL;

    for (uint64_t i = 0; i < samples; i++) {
        uint64_t r1 = lcg_next(state);
        uint64_t r2 = lcg_next(state);
        double x = (double)(r1 >> 11) * (1.0 / 9007199254740992.0);
        double y = (double)(r2 >> 11) * (1.0 / 9007199254740992.0);
        double d = x * x + y * y;
        if (d <= 1.0) {
            inside++;
        }
    }

    volatile double pi = 4.0 * (double)inside / (double)samples;
    (void)pi;
    return 0;
}
