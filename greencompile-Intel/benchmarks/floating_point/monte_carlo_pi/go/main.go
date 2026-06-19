package main

func lcgNext(state uint64) uint64 {
	return state*6364136223846793005 + 1
}

func main() {
	const samples uint64 = 500000000
	var inside uint64
	var state uint64 = 1
	const scale = 1.0 / 9007199254740992.0

	for i := uint64(0); i < samples; i++ {
		state = lcgNext(state)
		r1 := state
		state = lcgNext(state)
		r2 := state
		x := float64(r1>>11) * scale
		y := float64(r2>>11) * scale
		d := x*x + y*y
		if d <= 1.0 {
			inside++
		}
	}

	pi := 4.0 * float64(inside) / float64(samples)
	_ = pi
}
