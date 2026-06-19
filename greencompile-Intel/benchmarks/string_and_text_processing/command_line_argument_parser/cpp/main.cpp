#include <cstring>
#include <string>

int main(int argc, char **argv) {
    std::string mode = "default";
    std::string name = "unknown";
    int size = 0;
    int repeat = 0;
    int verbose = 0;

    for (int i = 1; i < argc; i++) {
        if (std::strcmp(argv[i], "--mode") == 0 && i + 1 < argc) {
            mode = argv[++i];
        } else if (std::strcmp(argv[i], "--name") == 0 && i + 1 < argc) {
            name = argv[++i];
        } else if (std::strcmp(argv[i], "--size") == 0 && i + 1 < argc) {
            size = std::atoi(argv[++i]);
        } else if (std::strcmp(argv[i], "--repeat") == 0 && i + 1 < argc) {
            repeat = std::atoi(argv[++i]);
        } else if (std::strcmp(argv[i], "--verbose") == 0) {
            verbose = 1;
        }
    }

    volatile int sink = static_cast<int>(mode.size() + name.size()) + size + repeat + verbose;
    (void)sink;
    return 0;
}
