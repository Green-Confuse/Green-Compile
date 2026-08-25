fn f(x: f64) -> f64 {
    4.0 / (1.0 + x * x)
}

fn simpson(a: f64, b: f64, mut n: i32) -> f64 {
    if n % 2 != 0 {
        n += 1;
    }
    let h = (b - a) / (n as f64);
    let mut sum = f(a) + f(b);
    for i in 1..n {
        let x = a + h * (i as f64);
        if i % 2 == 0 {
            sum += 2.0 * f(x);
        } else {
            sum += 4.0 * f(x);
        }
    }
    sum * h / 3.0
}

fn trapezoidal(a: f64, b: f64, n: i32) -> f64 {
    let h = (b - a) / (n as f64);
    let mut sum = 0.5 * (f(a) + f(b));
    for i in 1..n {
        let x = a + h * (i as f64);
        sum += f(x);
    }
    sum * h
}

fn main() {
    let a = 0.0;
    let b = 1.0;
    let n = 50_000_000;
    let _s = simpson(a, b, n);
    let _t = trapezoidal(a, b, n);
}
