const ROUNDS: usize = 20000;

fn rol(v: u32, n: u32) -> u32 {
    (v << n) | (v >> (32 - n))
}

fn sha1(msg: &[u8]) -> [u8; 20] {
    let mut h0: u32 = 0x67452301;
    let mut h1: u32 = 0xEFCDAB89;
    let mut h2: u32 = 0x98BADCFE;
    let mut h3: u32 = 0x10325476;
    let mut h4: u32 = 0xC3D2E1F0;

    let bit_len: u64 = (msg.len() as u64) * 8;
    let mut total = msg.len() + 1 + 8;
    let pad = (64 - (total % 64)) % 64;
    total += pad;

    let mut block = [0u8; 64];
    let mut off = 0usize;
    while off < total {
        for i in 0..64 {
            let idx = off + i;
            if idx < msg.len() {
                block[i] = msg[idx];
            } else if idx == msg.len() {
                block[i] = 0x80;
            } else if idx < total - 8 {
                block[i] = 0x00;
            } else {
                let shift = (total - 1 - idx) * 8;
                block[i] = (bit_len >> shift) as u8;
            }
        }

        let mut w = [0u32; 80];
        for i in 0..16 {
            let j = i * 4;
            w[i] = ((block[j] as u32) << 24)
                | ((block[j + 1] as u32) << 16)
                | ((block[j + 2] as u32) << 8)
                | (block[j + 3] as u32);
        }
        for i in 16..80 {
            w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
        }

        let mut a = h0;
        let mut b = h1;
        let mut c = h2;
        let mut d = h3;
        let mut e = h4;

        for i in 0..80 {
            let (f, k) = if i < 20 {
                ((b & c) | (!b & d), 0x5A827999)
            } else if i < 40 {
                (b ^ c ^ d, 0x6ED9EBA1)
            } else if i < 60 {
                ((b & c) | (b & d) | (c & d), 0x8F1BBCDC)
            } else {
                (b ^ c ^ d, 0xCA62C1D6)
            };
            let temp = rol(a, 5)
                .wrapping_add(f)
                .wrapping_add(e)
                .wrapping_add(k)
                .wrapping_add(w[i]);
            e = d;
            d = c;
            c = rol(b, 30);
            b = a;
            a = temp;
        }

        h0 = h0.wrapping_add(a);
        h1 = h1.wrapping_add(b);
        h2 = h2.wrapping_add(c);
        h3 = h3.wrapping_add(d);
        h4 = h4.wrapping_add(e);

        off += 64;
    }

    let mut out = [0u8; 20];
    let h = [h0, h1, h2, h3, h4];
    for i in 0..5 {
        out[i * 4] = (h[i] >> 24) as u8;
        out[i * 4 + 1] = (h[i] >> 16) as u8;
        out[i * 4 + 2] = (h[i] >> 8) as u8;
        out[i * 4 + 3] = h[i] as u8;
    }
    out
}

fn main() {
    let msg = b"GreenCompile SHA-1 pure implementation benchmark input.";
    let mut checksum: u8 = 0;
    for i in 0..ROUNDS {
        let out = sha1(msg);
        checksum ^= out[i % 20];
    }
    if checksum == 0 {
        print!("");
    }
}
