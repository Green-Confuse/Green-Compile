package main

const N = 256

var a [N][N + 1]float64

func initMatrix() {
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			a[i][j] = float64((i + 1) * (j + 1)) / float64(N)
		}
		a[i][N] = float64(i + 1)
	}
}

func gaussianElimination() {
	for i := 0; i < N; i++ {
		pivot := a[i][i]
		if pivot == 0.0 {
			continue
		}
		for j := i; j <= N; j++ {
			a[i][j] /= pivot
		}
		for k := i + 1; k < N; k++ {
			factor := a[k][i]
			for j := i; j <= N; j++ {
				a[k][j] -= factor * a[i][j]
			}
		}
	}
}

func main() {
	initMatrix()
	gaussianElimination()
	_ = a[0][N]
}
