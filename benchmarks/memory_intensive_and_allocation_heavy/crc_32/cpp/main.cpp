#include <cstdint>
#include <iomanip>
#include <iostream>
#include <cstring>

// Generate CRC-32 lookup table at runtime
std::uint32_t crc_table[256];

void init_crc_table() {
    for (std::uint32_t n = 0; n < 256; ++n) {
        std::uint32_t c = n;
        for (int k = 0; k < 8; ++k) {
            if (c & 1)
                c = 0xedb88320 ^ (c >> 1);
            else
                c >>= 1;
        }
        crc_table[n] = c;
    }
}

std::uint32_t crc32(const char* data, std::size_t length) {
    std::uint32_t crc = 0xFFFFFFFF;
    for (std::size_t i = 0; i < length; ++i) {
        std::uint8_t byte = static_cast<std::uint8_t>(data[i]);
        crc = crc_table[(crc ^ byte) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

int main() {
    init_crc_table();
    const char* str = "The quick brown fox jumps over the lazy dog";
    std::cout << std::hex << std::setw(8) << std::setfill('0') << crc32(str, std::strlen(str)) << '\n';
    return 0;
}