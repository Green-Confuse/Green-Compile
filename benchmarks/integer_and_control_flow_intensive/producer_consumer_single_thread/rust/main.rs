const CAPACITY: usize = 256;
const ITEMS_PER_ROUND: i32 = 5000;
const ROUNDS: i32 = 200;

fn main() {
    let mut buffer = [0i32; CAPACITY];
    let mut head = 0usize;
    let mut tail = 0usize;
    let mut count = 0usize;
    let mut checksum: i64 = 0;

    for r in 0..ROUNDS {
        let mut produced = 0;
        let mut consumed = 0;
        while consumed < ITEMS_PER_ROUND {
            if produced < ITEMS_PER_ROUND && count < CAPACITY {
                buffer[tail] = produced + r;
                tail = (tail + 1) % CAPACITY;
                count += 1;
                produced += 1;
            }
            if count > 0 {
                let value = buffer[head];
                head = (head + 1) % CAPACITY;
                count -= 1;
                checksum += value as i64;
                consumed += 1;
            }
        }
    }

    if checksum == 0 {
        print!("");
    }
}
