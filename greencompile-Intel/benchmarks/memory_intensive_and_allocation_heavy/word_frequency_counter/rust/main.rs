use std::collections::HashMap;

const TEXT: &str = "GreenCompile evaluates energy efficiency across CPU architectures. \
The word frequency counter parses text and counts repeated words. \
This benchmark stresses string handling, hashing, and memory access patterns.";

fn count_words(freq: &mut HashMap<String, usize>, text: &str) {
    let mut buf = String::with_capacity(32);
    for c in text.chars().chain(std::iter::once('\0')) {
        if c.is_ascii_alphanumeric() {
            buf.push(c.to_ascii_lowercase());
        } else if !buf.is_empty() {
            *freq.entry(buf.clone()).or_insert(0) += 1;
            buf.clear();
        }
    }
}

fn main() {
    let mut freq: HashMap<String, usize> = HashMap::new();
    for _ in 0..500 {
        count_words(&mut freq, TEXT);
    }

    let mut checksum: usize = 0;
    for (k, v) in &freq {
        checksum += v * k.len();
    }
    if checksum == 0 {
        print!("");
    }
}
