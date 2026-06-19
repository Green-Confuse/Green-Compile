#!/usr/bin/env python3
"""
scale_benchmarks.py
====================
Patches all benchmark source files in-place to use larger workload sizes,
addressing Reviewer Comment #3 (millisecond-scale benchmarks dominated by
OS/runtime startup overhead).

Target: ≥ 500 ms runtime on the FASTEST platform (AMD/Intel x86-64 -O2).
        ARM (Raspberry Pi 5) will naturally take 2-3× longer — that is the
        measurement, not a problem to fix.

Run ONCE from the repo root (greencompile-amd / greencompile-arm / greencompile-intel):
    python scripts/scale_benchmarks.py

Or do a dry run to preview all changes without writing:
    python scripts/scale_benchmarks.py --dry-run

Benchmarks modified and their rationale:
  towers_of_hanoi       N=20 → N=27    (~128× work, ~900 ms on AMD)
  monte_carlo_pi        10M  → 500M    (50×, ~500 ms on AMD C)
  newton_raphson        1 call → 100K  (100K loop over different seeds)
  numerical_integration n=1M → n=50M  (50×, ~300 ms on AMD)
  gaussian_elimination  N=128 → N=256  (8× work, O(N³), ~300 ms on AMD)
  matrix_multiplication tiny → 1M loop (1M × existing matrix = ~500 ms)
  palindrome_detection  r=2K → r=200K  (100×, ~500 ms)
  anagram_checker       r=2K → r=200K  (100×, ~700 ms)
  sha1_pure             200  → 20K     (100×, ~400 ms)
"""

import re
import sys
import argparse
from pathlib import Path

DRY_RUN = False

def patch_file(path: Path, replacements: list[tuple[str, str]]):
    """Apply (old_text, new_text) replacements to a file."""
    if not path.exists():
        print(f"  SKIP (not found): {path}")
        return
    content = path.read_text()
    new_content = content
    for old, new in replacements:
        if old in new_content:
            new_content = new_content.replace(old, new, 1)
            print(f"  PATCH: {path.name}  «{old}» → «{new}»")
        else:
            print(f"  WARN:  {path.name}  pattern not found: «{old}»")
    if new_content != content:
        if not DRY_RUN:
            path.write_text(new_content)
    else:
        print(f"  INFO:  {path.name}  no changes needed")


def patch_newton_raphson_c(path: Path):
    """Replace single-value newton_raphson with a 100K-iteration loop."""
    if not path.exists():
        return
    old = '''int main(void) {
    double x = 12345.6789;
    volatile double root = newton_sqrt(x);
    (void)root;
    return 0;
}'''
    new = '''int main(void) {
    /* [SCALED] Loop over 100000 seed values — ensures >500ms runtime */
    volatile double sink = 0.0;
    for (int i = 1; i <= 100000; i++) {
        double x = (double)i * 0.123456789;
        sink += newton_sqrt(x);
    }
    (void)sink;
    return 0;
}'''
    content = path.read_text()
    if old in content:
        print(f"  PATCH: {path.name}  newton_raphson main() scaled to 100K loop")
        if not DRY_RUN:
            path.write_text(content.replace(old, new, 1))
    else:
        print(f"  WARN:  {path.name}  newton_raphson pattern not found")


def patch_newton_raphson_rust(path: Path):
    if not path.exists():
        return
    old = '''fn main() {
    let x = 12345.6789;
    let _root = newton_sqrt(x);
}'''
    new = '''fn main() {
    // [SCALED] Loop over 100000 seed values
    let mut sink: f64 = 0.0;
    for i in 1..=100_000u32 {
        let x = (i as f64) * 0.123456789;
        sink += newton_sqrt(x);
    }
    let _ = sink;
}'''
    content = path.read_text()
    if old in content:
        print(f"  PATCH: {path.name}  newton_raphson main() scaled to 100K loop")
        if not DRY_RUN:
            path.write_text(content.replace(old, new, 1))
    else:
        print(f"  WARN:  {path.name}  newton_raphson rust pattern not found")


def patch_newton_raphson_go(path: Path):
    if not path.exists():
        return
    content = path.read_text()
    old = '''func main() {
\tx := 12345.6789
\t_root := newtonSqrt(x)
\t_ = _root
}'''
    # Try alternate formatting
    alts = [
        ('func main() {\n\tx := 12345.6789\n\t_root := newtonSqrt(x)\n\t_ = _root\n}',
         'func main() {\n\t// [SCALED] 100K loop\n\tvar sink float64\n\tfor i := 1; i <= 100000; i++ {\n\t\tx := float64(i) * 0.123456789\n\t\tsink += newtonSqrt(x)\n\t}\n\t_ = sink\n}'),
    ]
    patched = False
    for o, n in alts:
        if o in content:
            print(f"  PATCH: {path.name}  newton_raphson go scaled to 100K loop")
            if not DRY_RUN:
                path.write_text(content.replace(o, n, 1))
            patched = True
            break
    if not patched:
        # Try regex fallback
        new_main = ('func main() {\n'
                    '\t// [SCALED] 100K loop\n'
                    '\tvar sink float64\n'
                    '\tfor i := 1; i <= 100000; i++ {\n'
                    '\t\tx := float64(i) * 0.123456789\n'
                    '\t\tsink += newtonSqrt(x)\n'
                    '\t}\n'
                    '\t_ = sink\n'
                    '}')
        new_content = re.sub(r'func main\(\) \{[^}]+\}', new_main, content, flags=re.DOTALL)
        if new_content != content:
            print(f"  PATCH: {path.name}  newton_raphson go (regex)")
            if not DRY_RUN:
                path.write_text(new_content)
        else:
            print(f"  WARN:  {path.name}  newton_raphson go pattern not found")


def patch_newton_raphson_java(path: Path):
    if not path.exists():
        return
    content = path.read_text()
    old_pattern = r'public static void main\(String\[\] args\) \{[^}]+\}'
    new_main = (
        'public static void main(String[] args) {\n'
        '        // [SCALED] 100K loop\n'
        '        double sink = 0.0;\n'
        '        for (int i = 1; i <= 100000; i++) {\n'
        '            double x = (double)i * 0.123456789;\n'
        '            sink += newtonSqrt(x);\n'
        '        }\n'
        '        if (sink == 0.0) System.out.print("");\n'
        '    }'
    )
    new_content = re.sub(old_pattern, new_main, content, flags=re.DOTALL)
    if new_content != content:
        print(f"  PATCH: {path.name}  newton_raphson java scaled")
        if not DRY_RUN:
            path.write_text(new_content)
    else:
        print(f"  WARN:  {path.name}  newton_raphson java pattern not found")


def patch_matrix_mult_c(path: Path):
    """Wrap matrix multiplication in a 1M iteration loop."""
    if not path.exists():
        return
    content = path.read_text()
    old = '    mat_mult(4,4,3,a,b,c);\n    mat_show(4,3,c);\n    return 0;'
    new = (
        '    /* [SCALED] 1M repetitions — eliminates startup-dominated measurement */\n'
        '    for (int iter = 0; iter < 1000000; iter++) {\n'
        '        mat_mult(4,4,3,a,b,c);\n'
        '    }\n'
        '    volatile double sink = c[0];\n'
        '    (void)sink;\n'
        '    return 0;'
    )
    if old in content:
        print(f"  PATCH: {path.name}  matrix_mult wrapped in 1M loop")
        if not DRY_RUN:
            path.write_text(content.replace(old, new, 1))
    else:
        print(f"  WARN:  {path.name}  matrix_mult C loop pattern not found")


def patch_matrix_mult_rust(path: Path):
    if not path.exists():
        return
    content = path.read_text()
    old = '    let c = Matrix::mult_m(a, b);\n    \n\n    c.print();'
    new = (
        '    // [SCALED] 1M repetitions\n'
        '    let mut last = 0.0f32;\n'
        '    for _ in 0..1_000_000 {\n'
        '        let c = Matrix::mult_m(\n'
        '            Matrix { dat: a.dat },\n'
        '            Matrix { dat: b.dat },\n'
        '        );\n'
        '        last = c.dat[0][0];\n'
        '    }\n'
        '    let _ = last;'
    )
    if old in content:
        print(f"  PATCH: {path.name}  matrix_mult rust wrapped in 1M loop")
        if not DRY_RUN:
            path.write_text(content.replace(old, new, 1))
    else:
        # Simpler pattern — just add loop around the mult call
        old2 = '    \n\n    \n        let c = Matrix::mult_m(a, b);\n    \n\n    c.print();'
        new2 = ('    // [SCALED] 1M repetitions\n'
                '    let mut last = 0.0f32;\n'
                '    for _ in 0..1_000_000 {\n'
                '        let tmp = Matrix::mult_m(\n'
                '            Matrix { dat: [[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]] },\n'
                '            Matrix { dat: [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]] },\n'
                '        );\n'
                '        last = tmp.dat[0][0];\n'
                '    }\n'
                '    let _ = last;')
        new_content = re.sub(
            r'let\s+c\s*=\s*Matrix::mult_m\(a,\s*b\);.*?c\.print\(\);',
            ('// [SCALED] 1M repetitions\n'
             '    let mut last = 0.0f32;\n'
             '    for _ in 0..1_000_000 {\n'
             '        let tmp = Matrix::mult_m(\n'
             '            Matrix { dat: [[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]] },\n'
             '            Matrix { dat: [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]] },\n'
             '        );\n'
             '        last = tmp.dat[0][0];\n'
             '    }\n'
             '    let _ = last;'),
            content, flags=re.DOTALL
        )
        if new_content != content:
            print(f"  PATCH: {path.name}  matrix_mult rust (regex fallback)")
            if not DRY_RUN:
                path.write_text(new_content)
        else:
            print(f"  WARN:  {path.name}  matrix_mult rust pattern not found")


# ── Main scaling table ──────────────────────────────────────────────────────

BENCHMARKS_ROOT = Path("benchmarks")

def run_all_patches():
    bp = BENCHMARKS_ROOT

    print("\n── towers_of_hanoi  (N=20 → N=27) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("int N = 20", "int N = 27")]),
        ("cpp",  "main.cpp",  [("int N = 20", "int N = 27")]),
        ("rust", "main.rs",   [("let n = 20;", "let n = 27;")]),
        ("go",   "main.go",   [("N := 20",    "N := 27")]),
        ("java", "Main.java", [("int N = 20", "int N = 27")]),
    ]:
        patch_file(bp / "integer_and_control_flow_intensive/towers_of_hanoi" / lang / fname, patches)

    print("\n── monte_carlo_pi  (10M → 500M samples) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("10000000ULL",   "500000000ULL")]),
        ("cpp",  "main.cpp",  [("10000000",      "500000000"),
                               ("10'000'000",    "500'000'000")]),
        ("rust", "main.rs",   [("10_000_000",    "500_000_000"),
                               ("10000000",      "500000000")]),
        ("go",   "main.go",   [("10000000",      "500000000")]),
        ("java", "Main.java", [("10000000L",     "500000000L"),
                               ("10_000_000L",   "500_000_000L")]),
    ]:
        patch_file(bp / "floating_point/monte_carlo_pi" / lang / fname, patches)

    print("\n── newton_raphson  (single call → 100K loop) ──")
    patch_newton_raphson_c   (bp / "floating_point/newton_raphson/c/main.c")
    patch_newton_raphson_c   (bp / "floating_point/newton_raphson/cpp/main.cpp")
    patch_newton_raphson_rust(bp / "floating_point/newton_raphson/rust/main.rs")
    patch_newton_raphson_go  (bp / "floating_point/newton_raphson/go/main.go")
    patch_newton_raphson_java(bp / "floating_point/newton_raphson/java/Main.java")

    print("\n── numerical_integration  (n=1M → n=50M) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("int n = 1000000",   "int n = 50000000")]),
        ("cpp",  "main.cpp",  [("int n = 1000000",   "int n = 50000000"),
                               ("n = 1000000",       "n = 50000000")]),
        ("rust", "main.rs",   [("n: i32 = 1_000_000", "n: i32 = 50_000_000"),
                               ("1_000_000",         "50_000_000"),
                               ("1000000",           "50000000")]),
        ("go",   "main.go",   [("n := 1000000",      "n := 50000000"),
                               ("n = 1000000",       "n = 50000000")]),
        ("java", "Main.java", [("int n = 1000000",   "int n = 50000000"),
                               ("1000000",           "50000000")]),
    ]:
        patch_file(bp / "floating_point/numerical_integration" / lang / fname, patches)

    print("\n── gaussian_elimination  (N=128 → N=256) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("#define N 128",      "#define N 256")]),
        ("cpp",  "main.cpp",  [("#define N 128",      "#define N 256"),
                               ("const int N = 128",  "const int N = 256")]),
        ("rust", "main.rs",   [("const N: usize = 128", "const N: usize = 256")]),
        ("go",   "main.go",   [("const N = 128",      "const N = 256"),
                               ("N = 128",            "N = 256")]),
        ("java", "Main.java", [("static final int N = 128", "static final int N = 256"),
                               ("int N = 128",              "int N = 256")]),
    ]:
        patch_file(bp / "floating_point/gaussian_elimination" / lang / fname, patches)

    print("\n── matrix_multiplication  (tiny → 1M loop) ──")
    patch_matrix_mult_c   (bp / "floating_point/matrix_multiplication/c/main.c")
    patch_matrix_mult_c   (bp / "floating_point/matrix_multiplication/cpp/main.cpp")
    patch_matrix_mult_rust(bp / "floating_point/matrix_multiplication/rust/main.rs")

    print("\n── palindrome_detection  (r=2K → r=200K) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("r < 2000",  "r < 200000")]),
        ("cpp",  "main.cpp",  [("r < 2000",  "r < 200000")]),
        ("rust", "main.rs",   [("0..2000",   "0..200_000"), ("0..2_000", "0..200_000")]),
        ("go",   "main.go",   [("r < 2000",  "r < 200000")]),
        ("java", "Main.java", [("r < 2000",  "r < 200000")]),
    ]:
        patch_file(bp / "string_and_text_processing/palindrome_detection" / lang / fname, patches)

    print("\n── anagram_checker  (r=2K → r=200K) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("r < 2000",  "r < 200000")]),
        ("cpp",  "main.cpp",  [("r < 2000",  "r < 200000")]),
        ("rust", "main.rs",   [("0..2000",   "0..200_000"), ("0..2_000", "0..200_000")]),
        ("go",   "main.go",   [("r < 2000",  "r < 200000")]),
        ("java", "Main.java", [("r < 2000",  "r < 200000")]),
    ]:
        patch_file(bp / "string_and_text_processing/anagram_checker" / lang / fname, patches)

    print("\n── sha1_pure_implementation  (ROUNDS=200 → 20000) ──")
    for lang, fname, patches in [
        ("c",    "main.c",    [("#define ROUNDS 200",               "#define ROUNDS 20000")]),
        ("cpp",  "main.cpp",  [("#define ROUNDS 200",               "#define ROUNDS 20000"),
                               ("const int ROUNDS = 200",           "const int ROUNDS = 20000")]),
        ("rust", "main.rs",   [("const ROUNDS: usize = 200",        "const ROUNDS: usize = 20000")]),
        ("go",   "main.go",   [("const rounds = 200",               "const rounds = 20000"),
                               ("rounds := 200",                    "rounds := 20000"),
                               ("ROUNDS = 200",                     "ROUNDS = 20000")]),
        ("java", "Main.java", [("private static final int ROUNDS = 200",
                                "private static final int ROUNDS = 20000")]),
    ]:
        patch_file(bp / "string_and_text_processing/sha1_pure_implementation" / lang / fname, patches)

    print("\n✅ Scaling complete. Rebuild all binaries before re-running experiments:")
    print("   bash scripts/build_all.sh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    if DRY_RUN:
        print("DRY RUN — no files will be modified\n")

    if not BENCHMARKS_ROOT.exists():
        print(f"ERROR: '{BENCHMARKS_ROOT}' not found.")
        print("Run this script from the repo root (where benchmarks/ lives).")
        sys.exit(1)

    run_all_patches()
