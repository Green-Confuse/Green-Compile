struct Matrix {
    dat: [[f32; 3]; 3]
}

impl Matrix {
    pub fn mult_m(a: Matrix, b: Matrix) -> Matrix
    {
        let mut out = Matrix {
            dat: [[0., 0., 0.],
                  [0., 0., 0.],
                  [0., 0., 0.]
                  ]
        };

        for i in 0..3{
            for j in 0..3 {
                for k in 0..3 {
                    out.dat[i][j] += a.dat[i][k] * b.dat[k][j];
                }
            }
        }

        out
    }

    #[allow(dead_code)]
    pub fn print(self)
    {
        for i in 0..3 {
            for j in 0..3 {
                print!("{} ", self.dat[i][j]);
            }
            print!("\n");
        }
    }
}

fn main()
{
    let  a = Matrix {
        dat: [[1., 2., 3.],
              [4., 5., 6.],
              [7., 8., 9.]
              ]
    };

    let  b = Matrix {
        dat: [[1., 0., 0.],
              [0., 1., 0.],
              [0., 0., 1.]]
    };
	

    
        // [SCALED] 1M repetitions
    let mut last = 0.0f32;
    for _ in 0..1_000_000 {
        let c = Matrix::mult_m(
            Matrix { dat: a.dat },
            Matrix { dat: b.dat },
        );
        last = c.dat[0][0];
    }
    let _ = last;
}