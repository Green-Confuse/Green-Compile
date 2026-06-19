#include <array>
#include <cstdint>
#include <cstring>
#include <string>

static const int ROUNDS = 20000;

static uint32_t rol(uint32_t v, uint32_t n) { return (v << n) | (v >> (32 - n)); }

static std::array<uint8_t, 20> sha1(const uint8_t *msg, size_t len) {
    uint32_t h0 = 0x67452301;
    uint32_t h1 = 0xEFCDAB89;
    uint32_t h2 = 0x98BADCFE;
    uint32_t h3 = 0x10325476;
    uint32_t h4 = 0xC3D2E1F0;

    uint64_t bit_len = static_cast<uint64_t>(len) * 8;
    size_t total = len + 1 + 8;
    size_t pad = (64 - (total % 64)) % 64;
    total += pad;

    uint8_t block[128];
    size_t off = 0;
    while (off < total) {
        size_t chunk = 64;
        for (size_t i = 0; i < chunk; i++) {
            size_t idx = off + i;
            if (idx < len) {
                block[i] = msg[idx];
            } else if (idx == len) {
                block[i] = 0x80;
            } else if (idx < total - 8) {
                block[i] = 0x00;
            } else {
                size_t s = total - 1 - idx;
                block[i] = static_cast<uint8_t>(bit_len >> (s * 8));
            }
        }

        uint32_t w[80];
        for (int i = 0; i < 16; i++) {
            w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
                   (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(block[i * 4 + 3]));
        }
        for (int i = 16; i < 80; i++) {
            w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
        }

        uint32_t a = h0;
        uint32_t b = h1;
        uint32_t c = h2;
        uint32_t d = h3;
        uint32_t e = h4;

        for (int i = 0; i < 80; i++) {
            uint32_t f, k;
            if (i < 20) {
                f = (b & c) | (~b & d);
                k = 0x5A827999;
            } else if (i < 40) {
                f = b ^ c ^ d;
                k = 0x6ED9EBA1;
            } else if (i < 60) {
                f = (b & c) | (b & d) | (c & d);
                k = 0x8F1BBCDC;
            } else {
                f = b ^ c ^ d;
                k = 0xCA62C1D6;
            }
            uint32_t temp = rol(a, 5) + f + e + k + w[i];
            e = d;
            d = c;
            c = rol(b, 30);
            b = a;
            a = temp;
        }

        h0 += a;
        h1 += b;
        h2 += c;
        h3 += d;
        h4 += e;

        off += chunk;
    }

    std::array<uint8_t, 20> out{};
    uint32_t h[5] = {h0, h1, h2, h3, h4};
    for (int i = 0; i < 5; i++) {
        out[i * 4] = static_cast<uint8_t>(h[i] >> 24);
        out[i * 4 + 1] = static_cast<uint8_t>(h[i] >> 16);
        out[i * 4 + 2] = static_cast<uint8_t>(h[i] >> 8);
        out[i * 4 + 3] = static_cast<uint8_t>(h[i]);
    }
    return out;
}

int main() {
    const std::string msg = "GreenCompile SHA-1 pure implementation benchmark input.";
    uint8_t checksum = 0;
    for (int i = 0; i < ROUNDS; i++) {
        auto out = sha1(reinterpret_cast<const uint8_t *>(msg.data()), msg.size());
        checksum ^= out[i % 20];
    }
    volatile uint8_t sink = checksum;
    (void)sink;
    return 0;
}
