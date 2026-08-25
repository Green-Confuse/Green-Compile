#!/usr/bin/env python3
"""
add_checksums.py — make every benchmark print its result.

This single change fixes two of the three fatal measurement problems at once:

  (a) DEAD-CODE ELIMINATION. A value that is printed cannot be optimised away.
      This is a stronger guard than `volatile` or `black_box` because it is
      uniform across all five languages -- the previous suite used `volatile`
      in C/C++ but `let _x =` in Rust and `_ = x` in Go, which is precisely
      why Rust's Monte Carlo Pi ran 138x "faster" than C's.

  (b) IMPLEMENTATION PARITY. Once every implementation prints the same
      checksum, verify_parity.sh can prove that the five programs actually
      compute the same thing. The current suite does not: newton_raphson's C
      version solves 100,000 seeds while its C++ version solves one, and
      matrix_multiplication's C version does 10^6 repetitions while its C++
      version does a single 2x3 product.

Cost: one write() syscall at the end of a multi-second run. Negligible, and
the harness redirects stdout to /dev/null during measurement anyway.

Usage:
    python3 scripts/add_checksums.py --dry-run     # preview
    python3 scripts/add_checksums.py               # apply (.bak written)
    python3 scripts/add_checksums.py --report      # coverage table only

Anything this script cannot patch automatically is listed under MANUAL. That
list is not optional -- verify_parity.sh will fail on those benchmarks.
"""

import argparse
import glob
import os
import re
import sys

EXT = {"c": "main.c", "cpp": "main.cpp", "go": "main.go",
       "java": "Main.java", "rust": "main.rs"}

# ── Per-language rewrite rules ───────────────────────────────────────────────
# Each rule: (compiled regex, replacement builder). The builder receives the
# match and returns replacement text, or None to decline.

def _c_rules():
    return [
        # volatile double x = EXPR;  ... (void)x;
        (re.compile(r"(?m)^([ \t]*)volatile\s+(\w[\w \t*]*?)\s+(\w+)\s*=\s*(.+?);"),
         lambda m: f"{m.group(1)}{m.group(2)} {m.group(3)} = {m.group(4)};"),
        (re.compile(r"(?m)^[ \t]*\(\s*void\s*\)\s*(\w+)\s*;[ \t]*\n"),
         lambda m: ""),
    ]

def _rust_rules():
    return [
        (re.compile(r"(?m)^([ \t]*)let\s+_(\w+)\s*(:\s*[\w<>:\[\] ]+)?\s*=\s*(.+?);"),
         lambda m: f"{m.group(1)}let {m.group(2)}{m.group(3) or ''} = {m.group(4)};"),
        (re.compile(r"(?m)^([ \t]*)let\s+_\s*=\s*(.+?);"),
         lambda m: f"{m.group(1)}let __sink = {m.group(2)};"),
    ]

def _go_rules():
    return [
        (re.compile(r"(?m)^([ \t]*)_\s*=\s*(\w+)\s*$"), lambda m: ""),
        (re.compile(r"(?m)^([ \t]*)_\s*,\s*_\s*=\s*(.+?)$"), lambda m: ""),
        (re.compile(r"(?m)^([ \t]*)_\s*=\s*([a-zA-Z_]\w*\(.*\))\s*$"),
         lambda m: f"{m.group(1)}__sink := {m.group(2)}\n\t_ = __sink"),
    ]

RULES = {"c": _c_rules(), "cpp": _c_rules(), "rust": _rust_rules(), "go": _go_rules()}

# Names that look like a computed result, in preference order.
SINK_HINT = re.compile(
    r"\b(checksum|result|total|sum|sink|answer|count|inside|pi|root|s|t|out|val)\b")


def find_sinks(src, lang):
    """Return candidate result-variable names, best guess first."""
    names = []
    if lang in ("c", "cpp"):
        names += re.findall(r"volatile\s+[\w \t*]+?\s+(\w+)\s*=", src)
        names += re.findall(r"\(\s*void\s*\)\s*(\w+)\s*;", src)
    elif lang == "rust":
        names += [n for n in re.findall(r"let\s+_(\w+)\s*[:=]", src)]
    elif lang == "go":
        names += re.findall(r"^\s*_\s*=\s*(\w+)\s*$", src, re.M)
    elif lang == "java":
        names += re.findall(r"if\s*\(\s*(\w+)\s*==", src)
    seen, out = set(), []
    for n in names:
        if n and n not in seen:
            seen.add(n); out.append(n)
    return out


PRINT = {
    "c":    'printf("CHECKSUM=%.10g\\n", (double)({v}));',
    "cpp":  'std::printf("CHECKSUM=%.10g\\n", (double)({v}));',
    "go":   'fmt.Printf("CHECKSUM=%.10g\\n", float64({v}))',
    "rust": 'println!("CHECKSUM={{:.10}}", ({v}) as f64);',
    "java": 'System.out.printf("CHECKSUM=%.10g%n", (double)({v}));',
}

NEEDS_INCLUDE = {
    "c":   ("#include <stdio.h>", re.compile(r"#include\s*<stdio\.h>")),
    "cpp": ("#include <cstdio>",  re.compile(r"#include\s*<cstdio>")),
}


def patch(path, lang, dry):
    src = open(path, encoding="utf-8", errors="replace").read()
    orig = src

    if "CHECKSUM=" in src:
        return "already", None

    sinks = find_sinks(src, lang)
    if not sinks:
        return "manual", "no result variable found"

    v = sinks[0]

    # 1. un-discard the sink
    for rx, build in RULES.get(lang, []):
        src = rx.sub(lambda m: build(m), src)

    # 2. Java: replace the no-op conditional print with a real one
    if lang == "java":
        src = re.sub(
            r"(?m)^[ \t]*if\s*\([^)]*\)\s*\{\s*\n[ \t]*System\.out\.print\(\s*\"\"\s*\);\s*\n[ \t]*\}[ \t]*\n",
            "", src)

    # 3. insert the print before the end of main
    stmt = PRINT[lang].format(v=v)
    if lang in ("c", "cpp"):
        if not re.search(r"(?m)^[ \t]*return\s+0\s*;", src):
            return "manual", "no `return 0;` anchor in main"
        src = re.sub(r"(?m)^([ \t]*)return\s+0\s*;",
                     lambda m: f"{m.group(1)}{stmt}\n{m.group(1)}return 0;",
                     src, count=1)
        inc, has = NEEDS_INCLUDE[lang]
        if not has.search(src):
            src = inc + "\n" + src
    else:
        # last closing brace of the file closes main (go/rust) or the class (java)
        idx = src.rstrip().rfind("}")
        if lang == "java":
            idx = src.rstrip()[:idx].rfind("}")
        if idx < 0:
            return "manual", "could not locate end of main"
        indent = "\t" if lang == "go" else ("    " if lang == "rust" else "        ")
        src = src[:idx] + f"{indent}{stmt}\n" + src[idx:]
        if lang == "go" and not re.search(r'"fmt"', src):
            if re.search(r"(?m)^import\s*\(", src):
                src = re.sub(r"(?m)^import\s*\(", 'import (\n\t"fmt"', src, count=1)
            else:
                src = re.sub(r"(?m)^(package\s+\w+\s*\n)",
                             r'\1\nimport "fmt"\n', src, count=1)

    if src == orig:
        return "manual", "rules produced no change"
    if not dry:
        open(path + ".bak", "w").write(orig)
        open(path, "w").write(src)
    return "patched", v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="benchmarks")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    stats, manual = {}, []
    for lang, fn in EXT.items():
        for path in sorted(glob.glob(f"{a.root}/*/*/{lang}/{fn}")):
            algo = path.split("/")[2]
            st, info = patch(path, lang, a.dry_run or a.report)
            stats.setdefault(algo, {})[lang] = st
            if st == "manual":
                manual.append((algo, lang, path, info))

    langs = ["c", "cpp", "go", "java", "rust"]
    mark = {"patched": "  ok  ", "already": " skip ", "manual": "MANUAL"}
    print(f"{'benchmark':34s} " + " ".join(f"{l:^6s}" for l in langs))
    print("-" * 34 + " " + "-" * 34)
    for algo in sorted(stats):
        row = " ".join(f"{mark.get(stats[algo].get(l,'-'),'  --  '):^6s}" for l in langs)
        print(f"{algo:34s} {row}")

    n_ok = sum(1 for a_ in stats for l in stats[a_] if stats[a_][l] == "patched")
    print(f"\npatched: {n_ok}   manual: {len(manual)}")
    if manual:
        print("\nMANUAL INTERVENTION REQUIRED — verify_parity.sh will fail on these:")
        for algo, lang, path, why in manual:
            print(f"  {algo:32s} {lang:5s}  {why}")
            print(f"      {path}")
    if a.dry_run or a.report:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
