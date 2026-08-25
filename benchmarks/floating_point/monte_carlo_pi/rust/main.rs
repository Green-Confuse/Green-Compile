fn lcg_next(state: &mut u64) -> u64 {
    *state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
    *state
}

fn main() {
    let samples: u64 = 500_000_000;
    let mut inside: u64 = 0;
    let mut state: u64 = 1;
    let scale = 1.0 / 9007199254740992.0;

    for _ in 0..samples {
        let r1 = lcg_next(&mut state);
        let r2 = lcg_next(&mut state);
        let x = ((r1 >> 11) as f64) * scale;
        let y = ((r2 >> 11) as f64) * scale;
        let d = x * x + y * y;
        if d <= 1.0 {
            inside += 1;
        }
    }

    let _pi = 4.0 * (inside as f64) / (samples as f64);
}
