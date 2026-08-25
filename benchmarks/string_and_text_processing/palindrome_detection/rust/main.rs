const SAMPLES: [&str; 7] = [
    "A man, a plan, a canal, Panama!",
    "Never odd or even",
    "Not a palindrome",
    "Madam, I'm Adam",
    "racecar",
    "Able was I, ere I saw Elba",
    "palindrome",
];

fn is_palindrome(s: &str) -> bool {
    let chars: Vec<char> = s.chars().collect();
    if chars.is_empty() {
        return true;
    }
    let mut i = 0usize;
    let mut j = chars.len() - 1;
    while i < j {
        let a = chars[i];
        let b = chars[j];
        if !a.is_ascii_alphanumeric() {
            i += 1;
            continue;
        }
        if !b.is_ascii_alphanumeric() {
            if j == 0 {
                break;
            }
            j -= 1;
            continue;
        }
        if a.to_ascii_lowercase() != b.to_ascii_lowercase() {
            return false;
        }
        i += 1;
        if j == 0 {
            break;
        }
        j -= 1;
    }
    true
}

fn main() {
    let mut total = 0;
    for _ in 0..200_000 {
        for s in &SAMPLES {
            if is_palindrome(s) {
                total += 1;
            }
        }
    }
    if total == 0 {
        print!("");
    }
}
