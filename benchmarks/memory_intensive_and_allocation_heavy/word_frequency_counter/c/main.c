#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *word;
    int count;
} Entry;

static const char *TEXT =
    "GreenCompile evaluates energy efficiency across CPU architectures. "
    "The word frequency counter parses text and counts repeated words. "
    "This benchmark stresses string handling, hashing, and memory access patterns.";

static void add_word(Entry **entries, size_t *len, size_t *cap, const char *w) {
    for (size_t i = 0; i < *len; i++) {
        if (strcmp((*entries)[i].word, w) == 0) {
            (*entries)[i].count++;
            return;
        }
    }

    if (*len == *cap) {
        size_t new_cap = (*cap == 0) ? 16 : (*cap * 2);
        Entry *tmp = realloc(*entries, new_cap * sizeof(*tmp));
        if (!tmp) {
            exit(1);
        }
        *entries = tmp;
        *cap = new_cap;
    }

    (*entries)[*len].word = strdup(w);
    (*entries)[*len].count = 1;
    (*len)++;
}

static void count_words(Entry **entries, size_t *len, size_t *cap, const char *text) {
    char buf[64];
    size_t b = 0;

    for (const char *p = text; ; p++) {
        unsigned char c = (unsigned char)*p;
        if (isalnum(c)) {
            if (b + 1 < sizeof(buf)) {
                buf[b++] = (char)tolower(c);
            }
        } else {
            if (b > 0) {
                buf[b] = '\0';
                add_word(entries, len, cap, buf);
                b = 0;
            }
            if (c == '\0') {
                break;
            }
        }
    }
}

int main(void) {
    Entry *entries = NULL;
    size_t len = 0;
    size_t cap = 0;

    for (int i = 0; i < 500; i++) {
        count_words(&entries, &len, &cap, TEXT);
    }

    long checksum = 0;
    for (size_t i = 0; i < len; i++) {
        checksum += (long)entries[i].count * (long)strlen(entries[i].word);
    }
    volatile long sink = checksum;
    (void)sink;
    return 0;
}
