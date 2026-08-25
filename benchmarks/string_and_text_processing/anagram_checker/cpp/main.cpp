#include <array>
#include <cctype>
#include <string>
#include <utility>
#include <vector>

static const std::vector<std::pair<std::string, std::string>> PAIRS = {
    {"listen", "silent"},
    {"rail safety", "fairy tales"},
    {"dormitory", "dirty room"},
    {"the eyes", "they see"},
    {"not an anagram", "definitely not"},
    {"A gentleman", "elegant man"},
    {"Clint Eastwood", "old west action"}
};

static void normalize(const std::string &s, std::vector<unsigned char> &out) {
    out.clear();
    out.reserve(s.size());
    for (unsigned char c : s) {
        if (std::isalnum(c)) {
            out.push_back(static_cast<unsigned char>(std::tolower(c)));
        }
    }
}

static bool is_anagram(const std::string &a, const std::string &b) {
    std::vector<unsigned char> na;
    std::vector<unsigned char> nb;
    normalize(a, na);
    normalize(b, nb);
    if (na.size() != nb.size()) {
        return false;
    }

    std::array<int, 256> counts{};
    for (size_t i = 0; i < na.size(); i++) {
        counts[na[i]]++;
        counts[nb[i]]--;
    }
    for (int v : counts) {
        if (v != 0) {
            return false;
        }
    }
    return true;
}

int main() {
    int total = 0;
    for (int r = 0; r < 200000; r++) {
        for (const auto &p : PAIRS) {
            total += is_anagram(p.first, p.second) ? 1 : 0;
        }
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
