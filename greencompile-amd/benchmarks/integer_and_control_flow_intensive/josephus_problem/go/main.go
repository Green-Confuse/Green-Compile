package main

func josephus(n, k uint32) uint32 {
	var res uint32 = 0
	for i := uint32(1); i <= n; i++ {
		res = (res + k) % i
	}
	return res + 1
}

func main() {
	n := uint32(100000)
	k := uint32(3)
	_ = josephus(n, k)
}
