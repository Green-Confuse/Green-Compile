package main

func hanoi(n int, from int, to int, aux int) {
	if n == 0 {
		return
	}
	hanoi(n-1, from, aux, to)
	hanoi(n-1, aux, to, from)
}

func main() {
	N := 27
	hanoi(N, 1, 3, 2)
}
