package main

import "os"

func main() {
	mode := "default"
	name := "unknown"
	size := 0
	repeat := 0
	verbose := 0

	args := os.Args[1:]
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--mode":
			if i+1 < len(args) {
				i++
				mode = args[i]
			}
		case "--name":
			if i+1 < len(args) {
				i++
				name = args[i]
			}
		case "--size":
			if i+1 < len(args) {
				i++
				for _, c := range args[i] {
					if c >= '0' && c <= '9' {
						size = size*10 + int(c-'0')
					}
				}
			}
		case "--repeat":
			if i+1 < len(args) {
				i++
				for _, c := range args[i] {
					if c >= '0' && c <= '9' {
						repeat = repeat*10 + int(c-'0')
					}
				}
			}
		case "--verbose":
			verbose = 1
		}
	}

	_ = len(mode) + len(name) + size + repeat + verbose
}
