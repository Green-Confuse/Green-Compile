fn newton_sqrt(x: f64) -> f64 {
    let mut guess = x;
    for _ in 0..1000 {
        guess = 0.5 * (guess + x / guess);
    }
    guess
}

fn main() {
    // [SCALED] Loop over 100000 seed values
    let mut sink: f64 = 0.0;
    for i in 1..=100_000u32 {
        let x = (i as f64) * 0.123456789;
        sink += newton_sqrt(x);
    }
    let _ = sink;
}
