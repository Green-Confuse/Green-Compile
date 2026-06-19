const PAIRS: [(&str, &str); 7] = [
    ("listen", "silent"),
    ("rail safety", "fairy tales"),
    ("dormitory", "dirty room"),
    ("the eyes", "they see"),
    ("not an anagram", "definitely not"),
    ("A gentleman", "elegant man"),
    ("Clint Eastwood", "old west action"),
];

fn normalize(s: &str) -> Vec<char> {
    s.chars()
        .filter(|c| c.is_ascii_alphanumeric())
        .map(|c| c.to_ascii_lowercase())
        .collect()
}

fn is_anagram(a: &str, b: &str) -> bool {
    let na = normalize(a);
    let nb = normalize(b);
    if na.len() != nb.len() {
        return false;
    }
    let mut counts = [0i32; 256];
    for i in 0..na.len() {
        let ca = na[i] as u8;
        let cb = nb[i] as u8;
        counts[ca as usize] += 1;
        counts[cb as usize] -= 1;
    }
    counts.iter().all(|v| *v == 0)
}

fn main() {
    let mut total = 0;
    for _ in 0..200_000 {
        for (a, b) in &PAIRS {
            if is_anagram(a, b) {
                total += 1;
            }
        }
    }
    if total == 0 {
        print!("");
    }
}
