#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *A =
    "GCC and LLVM compilers optimize code; energy efficiency matters for modern CPUs.";
static const char *B =
    "Modern CPU energy efficiency depends on compiler optimizations and runtime behavior.";

static int lcs_len(const char *a, const char *b) {
    size_t n = strlen(a);
    size_t m = strlen(b);
    int *prev = calloc(m + 1, sizeof(*prev));
    int *curr = calloc(m + 1, sizeof(*curr));
    if (!prev || !curr) {
        free(prev);
        free(curr);
        return 0;
    }

    for (size_t i = 1; i <= n; i++) {
        curr[0] = 0;
        for (size_t j = 1; j <= m; j++) {
            if (a[i - 1] == b[j - 1]) {
                curr[j] = prev[j - 1] + 1;
            } else {
                curr[j] = (prev[j] > curr[j - 1]) ? prev[j] : curr[j - 1];
            }
        }
        memcpy(prev, curr, (m + 1) * sizeof(*prev));
    }
    int result = prev[m];
    free(prev);
    free(curr);
    return result;
}

int main(void) {
    int total = 0;
    for (int i = 0; i < 500; i++) {
        total += lcs_len(A, B);
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
