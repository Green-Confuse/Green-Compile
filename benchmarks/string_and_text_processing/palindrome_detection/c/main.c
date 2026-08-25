#include <ctype.h>
#include <stdio.h>
#include <string.h>

static const char *SAMPLES[] = {
    "A man, a plan, a canal, Panama!",
    "Never odd or even",
    "Not a palindrome",
    "Madam, I'm Adam",
    "racecar",
    "Able was I, ere I saw Elba",
    "palindrome"
};

static int is_palindrome(const char *s) {
    size_t i = 0;
    size_t j = strlen(s);
    if (j == 0) {
        return 1;
    }
    j--;

    while (i < j) {
        unsigned char a = (unsigned char)s[i];
        unsigned char b = (unsigned char)s[j];

        if (!isalnum(a)) {
            i++;
            continue;
        }
        if (!isalnum(b)) {
            j--;
            continue;
        }

        if (tolower(a) != tolower(b)) {
            return 0;
        }
        i++;
        j--;
    }
    return 1;
}

int main(void) {
    int total = 0;
    for (int r = 0; r < 200000; r++) {
        for (size_t i = 0; i < sizeof(SAMPLES) / sizeof(SAMPLES[0]); i++) {
            total += is_palindrome(SAMPLES[i]);
        }
    }
    volatile int sink = total;
    (void)sink;
    return 0;
}
