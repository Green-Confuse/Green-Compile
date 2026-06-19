package main

import "unicode"

var samples = []string{
	"A man, a plan, a canal, Panama!",
	"Never odd or even",
	"Not a palindrome",
	"Madam, I'm Adam",
	"racecar",
	"Able was I, ere I saw Elba",
	"palindrome",
}

func isPalindrome(s string) bool {
	r := []rune(s)
	i := 0
	j := len(r) - 1
	for i < j {
		a := r[i]
		b := r[j]
		if !unicode.IsLetter(a) && !unicode.IsDigit(a) {
			i++
			continue
		}
		if !unicode.IsLetter(b) && !unicode.IsDigit(b) {
			j--
			continue
		}
		if unicode.ToLower(a) != unicode.ToLower(b) {
			return false
		}
		i++
		j--
	}
	return true
}

func main() {
	total := 0
	for r := 0; r < 200000; r++ {
		for _, s := range samples {
			if isPalindrome(s) {
				total++
			}
		}
	}
	_ = total
}
