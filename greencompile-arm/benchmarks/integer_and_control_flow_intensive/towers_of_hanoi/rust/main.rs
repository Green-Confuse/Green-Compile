fn hanoi(n: i32, from: i32, to: i32, aux: i32) {
    if n == 0 {
        return;
    }
    hanoi(n - 1, from, aux, to);
    hanoi(n - 1, aux, to, from);
}

fn main() {
    let n = 27;
    hanoi(n, 1, 3, 2);
}
