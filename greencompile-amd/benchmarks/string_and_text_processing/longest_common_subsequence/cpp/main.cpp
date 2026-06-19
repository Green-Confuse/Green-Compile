#include <string>
#include <vector>

static const std::string A =
    "GCC and LLVM compilers optimize code; energy efficiency matters for modern CPUs.";
static const std::string B =
    "Modern CPU energy efficiency depends on compiler optimizations and runtime behavior.";

static int lcs_len(const std::string &a, const std::string &b) {
    const size_t n = a.size();
    const size_t m = b.size();
    std::vector<int> prev(m + 1, 0);
    std::vector<int> curr(m + 1, 0);

    for (size_t i = 1; i <= n; i++) {
        curr[0] = 0;
        for (size_t j = 1; j <= m; j++) {
            if (a[i - 1] == b[j - 1]) {
                curr[j] = prev[j - 1] + 1;
            } else {
                curr[j] = (prev[j] > curr[j - 1]) ? prev[j] : curr[j - 1];
            }
        }
        prev.swap(curr);
    }
    return prev[m];
}

int main() {
    int total = 0;
    for (int i = 0; i < 500; i++) {
        total += lcs_len(A, B);
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
