const A: &str = "GCC and LLVM compilers optimize code; energy efficiency matters for modern CPUs.";
const B: &str =
    "Modern CPU energy efficiency depends on compiler optimizations and runtime behavior.";

fn lcs_len(a: &str, b: &str) -> usize {
    let a_bytes = a.as_bytes();
    let b_bytes = b.as_bytes();
    let n = a_bytes.len();
    let m = b_bytes.len();
    let mut prev = vec![0usize; m + 1];
    let mut curr = vec![0usize; m + 1];

    for i in 1..=n {
        curr[0] = 0;
        for j in 1..=m {
            if a_bytes[i - 1] == b_bytes[j - 1] {
                curr[j] = prev[j - 1] + 1;
            } else if prev[j] > curr[j - 1] {
                curr[j] = prev[j];
            } else {
                curr[j] = curr[j - 1];
            }
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[m]
}

fn main() {
    let mut total = 0usize;
    for _ in 0..500 {
        total += lcs_len(A, B);
    }
    if total == 0 {
        print!("");
    }
}
