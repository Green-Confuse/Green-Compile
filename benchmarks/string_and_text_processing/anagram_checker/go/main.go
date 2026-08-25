package main

import "unicode"

type pair struct {
	a string
	b string
}

var pairs = []pair{
	{"listen", "silent"},
	{"rail safety", "fairy tales"},
	{"dormitory", "dirty room"},
	{"the eyes", "they see"},
	{"not an anagram", "definitely not"},
	{"A gentleman", "elegant man"},
	{"Clint Eastwood", "old west action"},
}

func normalize(s string) []rune {
	out := make([]rune, 0, len(s))
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			out = append(out, unicode.ToLower(r))
		}
	}
	return out
}

func isAnagram(a, b string) bool {
	na := normalize(a)
	nb := normalize(b)
	if len(na) != len(nb) {
		return false
	}
	counts := make(map[rune]int, len(na))
	for i := 0; i < len(na); i++ {
		counts[na[i]]++
		counts[nb[i]]--
	}
	for _, v := range counts {
		if v != 0 {
			return false
		}
	}
	return true
}

func main() {
	total := 0
	for r := 0; r < 200000; r++ {
		for _, p := range pairs {
			if isAnagram(p.a, p.b) {
				total++
			}
		}
	}
	_ = total
}
