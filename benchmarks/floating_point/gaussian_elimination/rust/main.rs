const N: usize = 256;

static mut A: [[f64; N + 1]; N] = [[0.0; N + 1]; N];

fn init_matrix() {
    unsafe {
        for i in 0..N {
            for j in 0..N {
                A[i][j] = ((i + 1) * (j + 1)) as f64 / (N as f64);
            }
            A[i][N] = (i + 1) as f64;
        }
    }
}

fn gaussian_elimination() {
    unsafe {
        for i in 0..N {
            let pivot = A[i][i];
            if pivot == 0.0 {
                continue;
            }
            for j in i..=N {
                A[i][j] /= pivot;
            }
            for k in (i + 1)..N {
                let factor = A[k][i];
                for j in i..=N {
                    A[k][j] -= factor * A[i][j];
                }
            }
        }
    }
}

fn main() {
    init_matrix();
    gaussian_elimination();
    let _x0 = unsafe { A[0][N] };
}
