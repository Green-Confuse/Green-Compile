#include <cctype>
#include <string>
#include <vector>

static const std::vector<std::string> SAMPLES = {
    "A man, a plan, a canal, Panama!",
    "Never odd or even",
    "Not a palindrome",
    "Madam, I'm Adam",
    "racecar",
    "Able was I, ere I saw Elba",
    "palindrome"
};

static bool is_palindrome(const std::string &s) {
    size_t i = 0;
    if (s.empty()) {
        return true;
    }
    size_t j = s.size() - 1;
    while (i < j) {
        unsigned char a = static_cast<unsigned char>(s[i]);
        unsigned char b = static_cast<unsigned char>(s[j]);
        if (!std::isalnum(a)) {
            i++;
            continue;
        }
        if (!std::isalnum(b)) {
            j--;
            continue;
        }
        if (std::tolower(a) != std::tolower(b)) {
            return false;
        }
        i++;
        j--;
    }
    return true;
}

int main() {
    int total = 0;
    for (int r = 0; r < 200000; r++) {
        for (const auto &s : SAMPLES) {
            total += is_palindrome(s) ? 1 : 0;
        }
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
