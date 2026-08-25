fn josephus(n: u32, k: u32) -> u32 {
    let mut res: u32 = 0;
    for i in 1..=n {
        res = (res + k) % i;
    }
    res + 1
}

fn main() {
    let n: u32 = 100000;
    let k: u32 = 3;
    let _survivor = josephus(n, k);
}
