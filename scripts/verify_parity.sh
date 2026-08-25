#!/usr/bin/env bash
# verify_parity.sh — prove the five implementations compute the same thing.
#
# This gate is what the manuscript's Section 3.2.1 claims was done ("automated
# diff-based comparison prior to any timing or energy measurement") but which
# demonstrably was not: newton_raphson's C version solves 100,000 seeds and its
# C++ version solves one; matrix_multiplication's C version does 10^6
# repetitions and its C++ version does a single 2x3 product and prints it.
#
# Requires every implementation to emit, on stdout, exactly:
#     CHECKSUM=<value>
#     WORKLOAD=<primary workload parameter>
#
# NOTHING MAY BE MEASURED UNTIL THIS SCRIPT EXITS 0.
#
# Usage:  bash scripts/verify_parity.sh [--tolerance 1e-9]

set -uo pipefail
TOL="${2:-1e-9}"
LANGS=(c cpp go java rust)
FAILED=0; PASSED=0; TOTAL=0

echo "=============================================================="
echo " Implementation parity gate"
echo "=============================================================="
printf "\n%-34s %-10s %s\n" "benchmark" "verdict" "detail"
printf -- "-%.0s" {1..92}; echo

for algo_dir in $(find benchmarks -mindepth 2 -maxdepth 2 -type d | sort); do
  algo=$(basename "$algo_dir")
  TOTAL=$((TOTAL+1))

  declare -A CK WL
  missing=""

  for lang in "${LANGS[@]}"; do
    if [[ "$lang" == "java" ]]; then
      [[ -f "$algo_dir/java/Main.class" ]] || { missing="$missing $lang"; continue; }
      out=$(cd "$algo_dir/java" && timeout 600 java -cp . Main 2>/dev/null)
    else
      bin="$algo_dir/$lang/benchmark"
      [[ -x "$bin" ]] || { missing="$missing $lang"; continue; }
      out=$(timeout 600 "$bin" 2>/dev/null)
    fi
    CK[$lang]=$(grep -m1 '^CHECKSUM=' <<<"$out" | cut -d= -f2- | tr -d '[:space:]')
    WL[$lang]=$(grep -m1 '^WORKLOAD=' <<<"$out" | cut -d= -f2- | tr -d '[:space:]')
    [[ -z "${CK[$lang]}" ]] && missing="$missing $lang(no-checksum)"
  done

  if [[ -n "$missing" ]]; then
    printf "%-34s %-10s %s\n" "$algo" "FAIL" "missing:$missing"
    FAILED=$((FAILED+1)); unset CK WL; continue
  fi

  verdict=$(python3 - "$TOL" "${CK[c]}" "${CK[cpp]}" "${CK[go]}" "${CK[java]}" "${CK[rust]}" \
                        "${WL[c]}" "${WL[cpp]}" "${WL[go]}" "${WL[java]}" "${WL[rust]}" <<'PY'
import sys
tol = float(sys.argv[1]); langs = ["c","cpp","go","java","rust"]
ck = dict(zip(langs, sys.argv[2:7])); wl = dict(zip(langs, sys.argv[7:12]))

# workload parameters must be IDENTICAL -- this is the newton_raphson bug
if len(set(wl.values())) > 1:
    print("FAIL|workload mismatch: " + ", ".join(f"{k}={v}" for k,v in wl.items()))
    sys.exit()

def num(x):
    try: return float(x)
    except ValueError: return None
vals = {k: num(v) for k, v in ck.items()}
if any(v is None for v in vals.values()):          # non-numeric: exact match
    if len(set(ck.values())) == 1: print("PASS|" + list(ck.values())[0][:40])
    else: print("FAIL|checksum mismatch: " + ", ".join(f"{k}={v[:18]}" for k,v in ck.items()))
    sys.exit()
lo, hi = min(vals.values()), max(vals.values())
scale = max(abs(lo), abs(hi), 1.0)
if (hi - lo) / scale <= tol: print(f"PASS|{lo:.10g}  (workload {wl['c']})")
else: print("FAIL|checksum mismatch: " + ", ".join(f"{k}={v:.8g}" for k,v in vals.items()))
PY
)

  status=${verdict%%|*}; detail=${verdict#*|}
  printf "%-34s %-10s %s\n" "$algo" "$status" "$detail"
  [[ "$status" == "PASS" ]] && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
  unset CK WL
done

echo
echo "=============================================================="
printf " %d/%d benchmarks verified equivalent\n" "$PASSED" "$TOTAL"
if [[ $FAILED -gt 0 ]]; then
  echo " $FAILED FAILED — do not measure until every one passes."
  echo "=============================================================="
  exit 1
fi
echo " Parity gate clear."
echo "=============================================================="
