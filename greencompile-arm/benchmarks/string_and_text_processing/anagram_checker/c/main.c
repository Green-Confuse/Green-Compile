#include <ctype.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const char *a;
    const char *b;
} Pair;

static const Pair PAIRS[] = {
    {"listen", "silent"},
    {"rail safety", "fairy tales"},
    {"dormitory", "dirty room"},
    {"the eyes", "they see"},
    {"not an anagram", "definitely not"},
    {"A gentleman", "elegant man"},
    {"Clint Eastwood", "old west action"}
};

static size_t normalize(const char *s, unsigned char *out, size_t cap) {
    size_t n = 0;
    for (; *s != '\0'; s++) {
        unsigned char c = (unsigned char)*s;
        if (isalnum(c)) {
            if (n < cap) {
                out[n++] = (unsigned char)tolower(c);
            }
        }
    }
    return n;
}

static int is_anagram(const char *a, const char *b) {
    unsigned char buf_a[256];
    unsigned char buf_b[256];
    size_t na = normalize(a, buf_a, sizeof(buf_a));
    size_t nb = normalize(b, buf_b, sizeof(buf_b));
    if (na != nb) {
        return 0;
    }

    int counts[256] = {0};
    for (size_t i = 0; i < na; i++) {
        counts[buf_a[i]]++;
        counts[buf_b[i]]--;
    }
    for (int i = 0; i < 256; i++) {
        if (counts[i] != 0) {
            return 0;
        }
    }
    return 1;
}

int main(void) {
    int total = 0;
    for (int r = 0; r < 200000; r++) {
        for (size_t i = 0; i < sizeof(PAIRS) / sizeof(PAIRS[0]); i++) {
            total += is_anagram(PAIRS[i].a, PAIRS[i].b);
        }
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
