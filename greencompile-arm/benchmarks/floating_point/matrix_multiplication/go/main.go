package main

import "fmt"

func main() {
    a := [][]float64{
        {1, 2, 3, 4},
        {5, 6, 7, 8},
    }
    b := [][]float64{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9},
        {10, 11, 12},
    }
    rows := len(a)
    cols := len(b[0])
    inner := len(b)
    c := make([][]float64, rows)
    for i := 0; i < rows; i++ {
        c[i] = make([]float64, cols)
        for j := 0; j < cols; j++ {
            sum := 0.0
            for k := 0; k < inner; k++ {
                sum += a[i][k] * b[k][j]
            }
            c[i][j] = sum
        }
    }
    fmt.Println(c)
}
