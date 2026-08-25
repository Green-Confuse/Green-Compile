package main

const N = 8

var board [N][N]int
var dx = [8]int{2, 1, -1, -2, -2, -1, 1, 2}
var dy = [8]int{1, 2, 2, 1, -1, -2, -2, -1}

func isValid(x, y int) bool {
	return x >= 0 && x < N && y >= 0 && y < N && board[y][x] == -1
}

func degree(x, y int) int {
	count := 0
	for i := 0; i < 8; i++ {
		nx := x + dx[i]
		ny := y + dy[i]
		if isValid(nx, ny) {
			count++
		}
	}
	return count
}

func solve(x, y, move int) bool {
	if move == N*N {
		return true
	}

	var candX [8]int
	var candY [8]int
	var candDeg [8]int
	count := 0

	for i := 0; i < 8; i++ {
		nx := x + dx[i]
		ny := y + dy[i]
		if isValid(nx, ny) {
			candX[count] = nx
			candY[count] = ny
			candDeg[count] = degree(nx, ny)
			count++
		}
	}

	for i := 0; i < count; i++ {
		best := i
		for j := i + 1; j < count; j++ {
			if candDeg[j] < candDeg[best] {
				best = j
			}
		}
		candX[i], candX[best] = candX[best], candX[i]
		candY[i], candY[best] = candY[best], candY[i]
		candDeg[i], candDeg[best] = candDeg[best], candDeg[i]

		nx := candX[i]
		ny := candY[i]
		board[ny][nx] = move
		if solve(nx, ny, move+1) {
			return true
		}
		board[ny][nx] = -1
	}

	return false
}

func main() {
	for y := 0; y < N; y++ {
		for x := 0; x < N; x++ {
			board[y][x] = -1
		}
	}
	board[0][0] = 0
	_ = solve(0, 0, 1)
}
