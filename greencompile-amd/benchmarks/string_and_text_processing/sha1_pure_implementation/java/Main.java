public class Main {
    private static final int ROUNDS = 20000;

    private static int rol(int v, int n) {
        return (v << n) | (v >>> (32 - n));
    }

    private static byte[] sha1(byte[] msg) {
        int h0 = 0x67452301;
        int h1 = 0xEFCDAB89;
        int h2 = 0x98BADCFE;
        int h3 = 0x10325476;
        int h4 = 0xC3D2E1F0;

        long bitLen = (long) msg.length * 8;
        int total = msg.length + 1 + 8;
        int pad = (64 - (total % 64)) % 64;
        total += pad;

        byte[] block = new byte[64];
        for (int off = 0; off < total; off += 64) {
            for (int i = 0; i < 64; i++) {
                int idx = off + i;
                if (idx < msg.length) {
                    block[i] = msg[idx];
                } else if (idx == msg.length) {
                    block[i] = (byte) 0x80;
                } else if (idx < total - 8) {
                    block[i] = 0;
                } else {
                    int shift = (total - 1 - idx) * 8;
                    block[i] = (byte) (bitLen >>> shift);
                }
            }

            int[] w = new int[80];
            for (int i = 0; i < 16; i++) {
                int j = i * 4;
                w[i] = ((block[j] & 0xFF) << 24) |
                       ((block[j + 1] & 0xFF) << 16) |
                       ((block[j + 2] & 0xFF) << 8) |
                       (block[j + 3] & 0xFF);
            }
            for (int i = 16; i < 80; i++) {
                w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
            }

            int a = h0;
            int b = h1;
            int c = h2;
            int d = h3;
            int e = h4;

            for (int i = 0; i < 80; i++) {
                int f;
                int k;
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
                int temp = rol(a, 5) + f + e + k + w[i];
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
        }

        byte[] out = new byte[20];
        int[] h = {h0, h1, h2, h3, h4};
        for (int i = 0; i < 5; i++) {
            int v = h[i];
            out[i * 4] = (byte) (v >>> 24);
            out[i * 4 + 1] = (byte) (v >>> 16);
            out[i * 4 + 2] = (byte) (v >>> 8);
            out[i * 4 + 3] = (byte) v;
        }
        return out;
    }

    public static void main(String[] args) {
        byte[] msg = "GreenCompile SHA-1 pure implementation benchmark input.".getBytes();
        byte checksum = 0;
        for (int i = 0; i < ROUNDS; i++) {
            byte[] out = sha1(msg);
            checksum ^= out[i % 20];
        }
        if (checksum == 0) {
            System.out.print("");
        }
    }
}
