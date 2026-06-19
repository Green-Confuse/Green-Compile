package main

const (
	capacity      = 256
	itemsPerRound = 5000
	rounds        = 200
)

func main() {
	var buffer [capacity]int
	head := 0
	tail := 0
	count := 0
	checksum := 0

	for r := 0; r < rounds; r++ {
		produced := 0
		consumed := 0
		for consumed < itemsPerRound {
			if produced < itemsPerRound && count < capacity {
				buffer[tail] = produced + r
				tail = (tail + 1) % capacity
				count++
				produced++
			}
			if count > 0 {
				value := buffer[head]
				head = (head + 1) % capacity
				count--
				checksum += value
				consumed++
			}
		}
	}

	_ = checksum
}
