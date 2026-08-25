package main

const aText = "GCC and LLVM compilers optimize code; energy efficiency matters for modern CPUs."
const bText = "Modern CPU energy efficiency depends on compiler optimizations and runtime behavior."

func lcsLen(a, b string) int {
	n := len(a)
	m := len(b)
	prev := make([]int, m+1)
	curr := make([]int, m+1)

	for i := 1; i <= n; i++ {
		curr[0] = 0
		for j := 1; j <= m; j++ {
			if a[i-1] == b[j-1] {
				curr[j] = prev[j-1] + 1
			} else {
				if prev[j] > curr[j-1] {
					curr[j] = prev[j]
				} else {
					curr[j] = curr[j-1]
				}
			}
		}
		copy(prev, curr)
	}
	return prev[m]
}

func main() {
	total := 0
	for i := 0; i < 500; i++ {
		total += lcsLen(aText, bText)
	}
	_ = total
}
