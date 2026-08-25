fn parse_int(s: &str) -> i32 {
    let mut value = 0;
    for c in s.chars() {
        if c.is_ascii_digit() {
            value = value * 10 + (c as i32 - '0' as i32);
        }
    }
    value
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut mode = "default".to_string();
    let mut name = "unknown".to_string();
    let mut size = 0;
    let mut repeat = 0;
    let mut verbose = 0;

    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--mode" => {
                if i + 1 < args.len() {
                    mode = args[i + 1].clone();
                    i += 1;
                }
            }
            "--name" => {
                if i + 1 < args.len() {
                    name = args[i + 1].clone();
                    i += 1;
                }
            }
            "--size" => {
                if i + 1 < args.len() {
                    size = parse_int(&args[i + 1]);
                    i += 1;
                }
            }
            "--repeat" => {
                if i + 1 < args.len() {
                    repeat = parse_int(&args[i + 1]);
                    i += 1;
                }
            }
            "--verbose" => {
                verbose = 1;
            }
            _ => {}
        }
        i += 1;
    }

    if mode.len() + name.len() + size as usize + repeat as usize + verbose as usize == 0 {
        print!("");
    }
}
