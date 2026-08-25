package main

import "encoding/binary"

const rounds = 20000

func rol(v uint32, n uint) uint32 {
	return (v << n) | (v >> (32 - n))
}

func sha1(msg []byte) [20]byte {
	h0 := uint32(0x67452301)
	h1 := uint32(0xEFCDAB89)
	h2 := uint32(0x98BADCFE)
	h3 := uint32(0x10325476)
	h4 := uint32(0xC3D2E1F0)

	bitLen := uint64(len(msg)) * 8
	total := len(msg) + 1 + 8
	pad := (64 - (total % 64)) % 64
	total += pad

	block := make([]byte, 64)
	for off := 0; off < total; off += 64 {
		for i := 0; i < 64; i++ {
			idx := off + i
			if idx < len(msg) {
				block[i] = msg[idx]
			} else if idx == len(msg) {
				block[i] = 0x80
			} else if idx < total-8 {
				block[i] = 0x00
			} else {
				shift := uint((total - 1 - idx) * 8)
				block[i] = byte(bitLen >> shift)
			}
		}

		var w [80]uint32
		for i := 0; i < 16; i++ {
			w[i] = binary.BigEndian.Uint32(block[i*4 : i*4+4])
		}
		for i := 16; i < 80; i++ {
			w[i] = rol(w[i-3]^w[i-8]^w[i-14]^w[i-16], 1)
		}

		a := h0
		b := h1
		c := h2
		d := h3
		e := h4

		for i := 0; i < 80; i++ {
			var f, k uint32
			switch {
			case i < 20:
				f = (b & c) | (^b & d)
				k = 0x5A827999
			case i < 40:
				f = b ^ c ^ d
				k = 0x6ED9EBA1
			case i < 60:
				f = (b & c) | (b & d) | (c & d)
				k = 0x8F1BBCDC
			default:
				f = b ^ c ^ d
				k = 0xCA62C1D6
			}
			temp := rol(a, 5) + f + e + k + w[i]
			e = d
			d = c
			c = rol(b, 30)
			b = a
			a = temp
		}

		h0 += a
		h1 += b
		h2 += c
		h3 += d
		h4 += e
	}

	var out [20]byte
	binary.BigEndian.PutUint32(out[0:4], h0)
	binary.BigEndian.PutUint32(out[4:8], h1)
	binary.BigEndian.PutUint32(out[8:12], h2)
	binary.BigEndian.PutUint32(out[12:16], h3)
	binary.BigEndian.PutUint32(out[16:20], h4)
	return out
}

func main() {
	msg := []byte("GreenCompile SHA-1 pure implementation benchmark input.")
	var checksum byte
	for i := 0; i < rounds; i++ {
		out := sha1(msg)
		checksum ^= out[i%20]
	}
	_ = checksum
}
