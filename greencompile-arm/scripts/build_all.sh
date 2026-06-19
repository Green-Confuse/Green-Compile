#!/usr/bin/env bash
# build_all.sh  —  FIXED (Reviewer Issue #2)
# ============================================
# Changes from original:
#   [FIX #2] C:    gcc → gcc -O2   (was -O0 by default)
#   [FIX #2] C++:  g++ → g++ -O2  (was -O0 by default)
#   [FIX #2] Rust: rustc → rustc -C opt-level=3 -C debuginfo=0
#                  (was debug profile by default; equivalent to --release)
#   UNCHANGED Go:  go build already applies standard optimisations by default
#   UNCHANGED Java: javac; runtime optimisation handled by JVM JIT
#
# Optimisation tier used: O2/O3 (production-equivalent)
# All five languages now compile at comparable optimisation levels.
# This is required for a valid cross-language energy comparison.
#
# If you want to preserve the original unoptimised results for comparison,
# run the original build_all.sh first, rename the results directory, then
# run this script for the optimised condition.

set -e
export PATH="$HOME/.cargo/bin:$PATH"

# ── Optimisation flags ────────────────────────────────────────────────────────
# Change these to O0/O1/O3 to reproduce different optimisation tiers.
GCC_OPT="-O2"          # was empty (= -O0)
GPP_OPT="-O2"          # was empty (= -O0)
RUST_OPT="-C opt-level=3 -C debuginfo=0"  # was empty (= debug profile)
# Go: no flag needed — go build applies standard opt by default
# Java: no flag needed — JIT compiles at runtime regardless of javac

echo "=== GreenCompile Build (OPTIMISED) ==="
echo "  C/C++ flag : $GCC_OPT"
echo "  Rust flag  : $RUST_OPT"
echo "  Go         : default (std opt)"
echo "  Java       : javac (JIT at runtime)"
echo ""

# ── C ─────────────────────────────────────────────────────────────────────────
find benchmarks -type f -name main.c | while read -r f; do
  d=$(dirname "$f")
  echo "gcc $GCC_OPT  -> $d/benchmark"
  # [FIX #2] -O2 added; -lm ensures math.h functions are linked on all systems
  gcc $GCC_OPT -lm "$f" -o "$d/benchmark"
done

# ── C++ ───────────────────────────────────────────────────────────────────────
find benchmarks -type f -name main.cpp | while read -r f; do
  d=$(dirname "$f")
  echo "g++ $GPP_OPT  -> $d/benchmark"
  # [FIX #2] -O2 added
  g++ $GPP_OPT "$f" -o "$d/benchmark"
done

# ── Go ────────────────────────────────────────────────────────────────────────
find benchmarks -type f -name main.go | while read -r f; do
  d=$(dirname "$f")
  echo "go build (std opt)  -> $d/benchmark"
  # UNCHANGED — go build already optimises by default
  (cd "$d" && go build -o benchmark main.go)
done

# ── Rust ──────────────────────────────────────────────────────────────────────
find benchmarks -type f -name main.rs | while read -r f; do
  d=$(dirname "$f")
  echo "rustc $RUST_OPT  -> $d/benchmark"
  # [FIX #2] opt-level=3 + no debug info (equivalent to cargo --release)
  rustc $RUST_OPT "$f" -o "$d/benchmark"
done

# ── Java ──────────────────────────────────────────────────────────────────────
find benchmarks -type f -name Main.java | while read -r f; do
  d=$(dirname "$f")
  echo "javac  -> $d/Main.class  (JIT applies at runtime)"
  # UNCHANGED — optimisation is JIT-applied, javac flags don't affect peak perf
  (cd "$d" && javac Main.java)
done

echo ""
echo "✅ Build done (optimised tier: C/C++ $GCC_OPT, Rust $RUST_OPT)."
