#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int is_flag(const char *arg, const char *flag) {
    return strcmp(arg, flag) == 0;
}

int main(int argc, char **argv) {
    const char *mode = "default";
    const char *name = "unknown";
    int size = 0;
    int repeat = 0;
    int verbose = 0;

    for (int i = 1; i < argc; i++) {
        if (is_flag(argv[i], "--mode") && i + 1 < argc) {
            mode = argv[++i];
        } else if (is_flag(argv[i], "--name") && i + 1 < argc) {
            name = argv[++i];
        } else if (is_flag(argv[i], "--size") && i + 1 < argc) {
            size = atoi(argv[++i]);
        } else if (is_flag(argv[i], "--repeat") && i + 1 < argc) {
            repeat = atoi(argv[++i]);
        } else if (is_flag(argv[i], "--verbose")) {
            verbose = 1;
        }
    }

    volatile int sink = (int)strlen(mode) + (int)strlen(name) + size + repeat + verbose;
    (void)sink;
    return 0;
}
