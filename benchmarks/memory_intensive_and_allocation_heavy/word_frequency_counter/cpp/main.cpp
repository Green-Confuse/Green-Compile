#include <cctype>
#include <iostream>
#include <string>
#include <unordered_map>

static const std::string TEXT =
    "GreenCompile evaluates energy efficiency across CPU architectures. "
    "The word frequency counter parses text and counts repeated words. "
    "This benchmark stresses string handling, hashing, and memory access patterns.";

static void count_words(std::unordered_map<std::string, int> &freq, const std::string &text) {
    std::string buf;
    buf.reserve(32);
    for (size_t i = 0; i <= text.size(); i++) {
        unsigned char c = (i < text.size()) ? static_cast<unsigned char>(text[i]) : '\0';
        if (std::isalnum(c)) {
            buf.push_back(static_cast<char>(std::tolower(c)));
        } else if (!buf.empty()) {
            freq[buf]++;
            buf.clear();
        }
    }
}

int main() {
    std::unordered_map<std::string, int> freq;
    for (int i = 0; i < 500; i++) {
        count_words(freq, TEXT);
    }

    long checksum = 0;
    for (const auto &kv : freq) {
        checksum += static_cast<long>(kv.second) * static_cast<long>(kv.first.size());
    }
    volatile long sink = checksum;
    (void)sink;
    return 0;
}
