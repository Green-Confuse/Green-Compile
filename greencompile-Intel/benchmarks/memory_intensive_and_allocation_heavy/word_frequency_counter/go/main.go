package main

import (
	"strings"
	"unicode"
)

const text = "GreenCompile evaluates energy efficiency across CPU architectures. " +
	"The word frequency counter parses text and counts repeated words. " +
	"This benchmark stresses string handling, hashing, and memory access patterns."

func countWords(freq map[string]int, s string) {
	var b strings.Builder
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			b.WriteRune(unicode.ToLower(r))
		} else if b.Len() > 0 {
			freq[b.String()]++
			b.Reset()
		}
	}
	if b.Len() > 0 {
		freq[b.String()]++
	}
}

func main() {
	freq := make(map[string]int)
	for i := 0; i < 500; i++ {
		countWords(freq, text)
	}

	checksum := 0
	for k, v := range freq {
		checksum += v * len(k)
	}
	_ = checksum
}
