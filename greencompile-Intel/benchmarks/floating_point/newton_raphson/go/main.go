package main

func newtonSqrt(x float64) float64 {
	guess := x
	for i := 0; i < 1000; i++ {
		guess = 0.5 * (guess + x/guess)
	}
	return guess
}

func main() {
	// [SCALED] 100K loop
	var sink float64
	for i := 1; i <= 100000; i++ {
		x := float64(i) * 0.123456789
		sink += newtonSqrt(x)
	}
	_ = sink
}
