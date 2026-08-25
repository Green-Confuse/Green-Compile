#!/usr/bin/env bash
# run_all_x86.sh — RAPL measurement harness for AMD and Intel  [CORRECTED]
# =============================================================================
# Replaces run_all_amd.sh and run_all_intel.sh (they were identical apart from
# a default string). Pass the platform name as $1.
#
# WHAT WAS WRONG BEFORE
# ---------------------
# The old measure_cmd() opened the energy window before the timing window:
#
#     e1=$(sudo cat "$ENERGY_PATH")     <-- energy window opens
#     t1=$(date +%s%N)                  <-- timing window opens (2 forks later)
#     bash -c "$cmd"
#     t2=$(date +%s%N)
#     e2=$(sudo cat "$ENERGY_PATH")     <-- energy window closes
#
# A full `sudo` invocation (PAM stack, sudoers parse, timestamp file) plus two
# `date` forks landed inside the energy numerator and outside the time
# denominator. Fitting E = E0 + P*T over the 100 published AMD configurations:
#
#     E = 0.4289 J + 6.803 W * T        R^2 = 0.948
#
# i.e. a CONSTANT 429 mJ added to every single measurement, equivalent to 63 ms
# of untimed work. On a 2 ms benchmark that offset IS the measurement, which is
# why the paper reports 76-99 W package power on 15 W and 28 W mobile parts.
#
# WHAT THIS VERSION DOES
# ----------------------
#   * `sudo chmod a+r` on the counter ONCE, at session start; no sudo per run.
#   * `read -r` (bash builtin) instead of `cat` -- forks nothing.
#   * ${EPOCHREALTIME} (bash builtin) instead of `date` -- forks nothing.
#   * Direct exec of the binary; no `bash -c` subshell.
#   * All arithmetic deferred to post-processing; no python3 in the loop.
#   * RAPL counter wraparound handled instead of discarded as FAIL.
#   * Idle baseline measured through the identical code path as the runs.
#   * Every run checked against the part's PL2; implausible power fails loudly.
#
# Usage:
#   bash scripts/run_all_x86.sh amd
#   bash scripts/run_all_x86.sh intel
# =============================================================================

set -uo pipefail

PLATFORM="${1:?usage: run_all_x86.sh <amd|intel>}"
REPS="${REPS:-10}"
WARMUP="${WARMUP:-3}"
JAVA_WARMUP="${JAVA_WARMUP:-3}"
IDLE_SECONDS="${IDLE_SECONDS:-30}"
BENCH_CPUS="${BENCH_CPUS:-0-2}"

# Package power ceiling used for the plausibility assertion (watts).
# AMD Ryzen 5 5500U: PPT ~25 W.   Intel i5-1135G7: PL2 ~64 W.
case "$PLATFORM" in
  amd)   PL_MAX="${PL_MAX:-30}"  ;;
  intel) PL_MAX="${PL_MAX:-70}"  ;;
  *) echo "FATAL: platform must be 'amd' or 'intel'"; exit 1 ;;
esac

RAPL_DIR="${RAPL_DIR:-/sys/class/powercap/intel-rapl:0}"
ENERGY_PATH="$RAPL_DIR/energy_uj"
MAX_PATH="$RAPL_DIR/max_energy_range_uj"
RUNS_CSV="results/raw/${PLATFORM}_runs.csv"
IDLE_FILE="results/processed/idle_power_w.txt"

mkdir -p results/raw results/processed

# ── Counter access, once ─────────────────────────────────────────────────────
[[ -r "$RAPL_DIR/name" ]] || { echo "FATAL: $RAPL_DIR not present"; exit 1; }
DOMAIN=$(cat "$RAPL_DIR/name")
echo "RAPL domain: $DOMAIN   ($RAPL_DIR)"

if ! read -r _probe < "$ENERGY_PATH" 2>/dev/null; then
  echo "Counter is root-only; granting read access for this session..."
  sudo chmod a+r "$ENERGY_PATH" || { echo "FATAL: cannot read $ENERGY_PATH"; exit 1; }
fi
read -r E_MAX < "$MAX_PATH"
echo "Counter wraps at ${E_MAX} uj"

command -v taskset >/dev/null || { echo "FATAL: taskset missing"; exit 1; }
if [[ "${BASH_VERSINFO[0]}" -lt 5 ]]; then
  echo "FATAL: bash >= 5.0 required for \$EPOCHREALTIME (found $BASH_VERSION)"; exit 1
fi

# ── Idle baseline, through the same read path as the measured runs ───────────
echo "Measuring idle baseline for ${IDLE_SECONDS}s (do not touch the machine)..."
read -r IE1 < "$ENERGY_PATH"; IT1=${EPOCHREALTIME/./}
sleep "$IDLE_SECONDS"
read -r IE2 < "$ENERGY_PATH"; IT2=${EPOCHREALTIME/./}
IDLE_POWER_W=$(awk -v e1="$IE1" -v e2="$IE2" -v t1="$IT1" -v t2="$IT2" -v m="$E_MAX" \
  'BEGIN{d=e2-e1; if(d<0) d+=m; printf "%.4f", (d/1e6)/((t2-t1)/1e6)}')
echo "Idle baseline: ${IDLE_POWER_W} W"
echo "$IDLE_POWER_W" > "$IDLE_FILE"

awk -v p="$IDLE_POWER_W" -v m="$PL_MAX" 'BEGIN{exit !(p>0 && p<m)}' || {
  echo "FATAL: idle power ${IDLE_POWER_W} W is outside (0, ${PL_MAX}) W."
  echo "       The machine is not idle, or the counter is being misread."
  exit 1; }

echo "platform,category,algorithm,language,run,t_start_us,t_end_us,e_start_uj,e_end_uj,e_max_uj,exit_code" > "$RUNS_CSV"

# ── Measurement: nothing but the exec sits between the two reads ─────────────
measure_one () {
  local cat="$1" algo="$2" lang="$3" run="$4"; shift 4
  local e1 e2 t1 t2 rc
  read -r e1 < "$ENERGY_PATH"; t1=${EPOCHREALTIME/./}
  taskset -c "$BENCH_CPUS" "$@" >/dev/null 2>/dev/null
  rc=$?
  t2=${EPOCHREALTIME/./}; read -r e2 < "$ENERGY_PATH"
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$PLATFORM" "$cat" "$algo" "$lang" "$run" "$t1" "$t2" "$e1" "$e2" "$E_MAX" "$rc" >> "$RUNS_CSV"
}

run_suite () {
  local cat="$1" algo="$2" lang="$3"; shift 3
  local w=$WARMUP
  [[ "$lang" == "java" ]] && w=$JAVA_WARMUP
  echo "  ${cat}/${algo}/${lang}  (warmup ${w}, reps ${REPS})"
  for _ in $(seq 1 "$w"); do
    taskset -c "$BENCH_CPUS" "$@" >/dev/null 2>/dev/null || true
  done
  for r in $(seq 1 "$REPS"); do measure_one "$cat" "$algo" "$lang" "$r" "$@"; done
}

echo ""
echo "=== Native binaries ==="
while IFS= read -r bin; do
  lang=$(basename "$(dirname "$bin")")
  algo=$(basename "$(dirname "$(dirname "$bin")")")
  cat=$(basename  "$(dirname "$(dirname "$(dirname "$bin")")")")
  run_suite "$cat" "$algo" "$lang" "$(realpath "$bin")"
done < <(find benchmarks -type f -name benchmark | sort)

echo ""
echo "=== Java ==="
while IFS= read -r cls; do
  d=$(dirname "$cls")
  algo=$(basename "$(dirname "$d")")
  cat=$(basename  "$(dirname "$(dirname "$d")")")
  run_suite "$cat" "$algo" "java" java -XX:+UseSerialGC -cp "$(realpath "$d")" Main
done < <(find benchmarks -type f -name Main.class | sort)

echo ""
echo "=== Reducing ==="
python3 scripts/reduce_x86.py \
  --runs "$RUNS_CSV" --idle "$IDLE_FILE" --pl-max "$PL_MAX" \
  --domain "$DOMAIN" --energy-path "$ENERGY_PATH" \
  --out "results/raw/${PLATFORM}_results.csv"

echo ""
echo "Done. Keep ${RUNS_CSV} -- it holds the raw counter values, which is the"
echo "auditable evidence that no arithmetic happened inside the timing window."
