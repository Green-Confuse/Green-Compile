package main

func f(x float64) float64 {
	return 4.0 / (1.0 + x*x)
}

func simpson(a, b float64, n int) float64 {
	if n%2 != 0 {
		n++
	}
	h := (b - a) / float64(n)
	sum := f(a) + f(b)
	for i := 1; i < n; i++ {
		x := a + h*float64(i)
		if i%2 == 0 {
			sum += 2.0 * f(x)
		} else {
			sum += 4.0 * f(x)
		}
	}
	return sum * h / 3.0
}

func trapezoidal(a, b float64, n int) float64 {
	h := (b - a) / float64(n)
	sum := 0.5 * (f(a) + f(b))
	for i := 1; i < n; i++ {
		x := a + h*float64(i)
		sum += f(x)
	}
	return sum * h
}

func main() {
	a := 0.0
	b := 1.0
	n := 50000000
	_ = simpson(a, b, n)
	_ = trapezoidal(a, b, n)
}
