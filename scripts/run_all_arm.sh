#!/usr/bin/env bash
# run_all_arm.sh — Raspberry Pi 5 measurement harness  [CORRECTED]
# =============================================================================
# What changed vs the previous version, and why:
#
#  1. ENERGY IS NOW ACTUALLY INTEGRATED.
#     Old: two vcgencmd samples, one before the run and one after it exited.
#          Neither was taken while the benchmark was running, so
#          energy_j = P_idle * T for all 1000 runs -- no workload signal.
#     New: pmic_sampler.py runs continuously for the whole session; this
#          script records t_start/t_end per run; integrate_energy.py slices
#          the sample stream and applies the composite trapezoidal rule.
#          This is what Eq. 16 of the manuscript describes.
#
#  2. NO FORKS INSIDE THE TIMING WINDOW.
#     Old: `bash -c "$cmd"` plus a python3 subprocess for every arithmetic op.
#     New: the binary is exec'd directly; all arithmetic moved to post-
#          processing. Timestamps come from bash's own $EPOCHREALTIME.
#
#  3. NO PER-RUN PYTHON.
#     Old: 4 python3 interpreter launches per measured run (~120 ms of
#          untimed work adjacent to a 2 ms benchmark).
#     New: this script writes only raw timestamps; all computation is batch.
#
#  4. CPU PINNING. Benchmark on core 0-2, sampler on core 3, so the sampler's
#     vcgencmd overhead does not contend with the workload.
#
#  5. UNDERSAMPLED RUNS ARE FAILED, NOT REPORTED. See integrate_energy.py.
#
# Prerequisites: run scripts/preflight_arm.sh first and fix anything it flags.
# =============================================================================

set -uo pipefail

RUNS_CSV="results/raw/arm_runs.csv"
SAMPLES_CSV="results/raw/pmic_samples.csv"
IDLE_FILE="results/processed/idle_power_w.txt"
SAMPLER_PID_FILE="/tmp/greencompile_sampler.pid"

REPS="${REPS:-10}"
WARMUP="${WARMUP:-3}"
JAVA_WARMUP="${JAVA_WARMUP:-3}"
SAMPLE_INTERVAL="${SAMPLE_INTERVAL:-0.005}"
BENCH_CPUS="${BENCH_CPUS:-0-2}"
SAMPLER_CPU="${SAMPLER_CPU:-3}"
IDLE_SECONDS="${IDLE_SECONDS:-30}"

mkdir -p results/raw results/processed

command -v vcgencmd >/dev/null || { echo "FATAL: vcgencmd not found"; exit 1; }
command -v taskset  >/dev/null || { echo "FATAL: taskset not found (apt install util-linux)"; exit 1; }

cleanup() {
  if [[ -f "$SAMPLER_PID_FILE" ]]; then
    kill "$(cat "$SAMPLER_PID_FILE")" 2>/dev/null || true
    sleep 1
    rm -f "$SAMPLER_PID_FILE"
  fi
}
trap cleanup EXIT INT TERM

# ── Start the continuous sampler ─────────────────────────────────────────────
echo "Starting PMIC sampler (interval ${SAMPLE_INTERVAL}s, pinned to CPU ${SAMPLER_CPU})..."
taskset -c "$SAMPLER_CPU" python3 scripts/pmic_sampler.py \
    --out "$SAMPLES_CSV" --interval "$SAMPLE_INTERVAL" &
echo $! > "$SAMPLER_PID_FILE"
sleep 3
[[ -s "$SAMPLES_CSV" ]] || { echo "FATAL: sampler produced no output"; exit 1; }

# ── Idle baseline: measured by the SAME sampler, same code path ──────────────
# The old harness used a different sampling path for the baseline than for the
# runs, which is how active power ended up below idle power.
echo "Measuring idle baseline for ${IDLE_SECONDS}s (stay off the machine)..."
IDLE_T0=$(date +%s%N)
sleep "$IDLE_SECONDS"
IDLE_T1=$(date +%s%N)
python3 - "$SAMPLES_CSV" "$IDLE_T0" "$IDLE_T1" "$IDLE_FILE" <<'PY'
import sys, pandas as pd
s, t0, t1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
d = pd.read_csv(s)
w = d[(d.t_ns >= t0) & (d.t_ns <= t1)].watts
if len(w) < 100:
    sys.exit(f"FATAL: only {len(w)} idle samples; sampler is too slow.")
open(out, "w").write(f"{w.mean():.4f}\n")
print(f"Idle baseline: {w.mean():.4f} W  (SD {w.std():.4f}, n={len(w)}, "
      f"range {w.min():.3f}-{w.max():.3f})")
PY
IDLE_POWER_W=$(cat "$IDLE_FILE")

echo "category,algorithm,language,run,t_start_ns,t_end_ns,exit_code" > "$RUNS_CSV"

# ── Measurement ──────────────────────────────────────────────────────────────
# The window contains ONLY the exec of the benchmark. $EPOCHREALTIME is a bash
# builtin (bash >= 5.0) and forks nothing.
measure_one () {
  local cat="$1" algo="$2" lang="$3" run="$4"; shift 4
  local t1 t2 rc
  t1=${EPOCHREALTIME/./}                     # microseconds, no fork
  taskset -c "$BENCH_CPUS" "$@" >/dev/null 2>/dev/null
  rc=$?
  t2=${EPOCHREALTIME/./}
  printf '%s,%s,%s,%s,%s,%s,%s\n' \
      "$cat" "$algo" "$lang" "$run" "${t1}000" "${t2}000" "$rc" >> "$RUNS_CSV"
}

run_suite () {
  local bin_desc="$1"; shift
  local cat="$1" algo="$2" lang="$3"; shift 3
  local w=$WARMUP
  [[ "$lang" == "java" ]] && w=$JAVA_WARMUP

  echo "  ${cat}/${algo}/${lang}  (warmup ${w}, reps ${REPS})"
  for _ in $(seq 1 "$w"); do
    taskset -c "$BENCH_CPUS" "$@" >/dev/null 2>/dev/null || true
  done
  for r in $(seq 1 "$REPS"); do
    measure_one "$cat" "$algo" "$lang" "$r" "$@"
  done
}

echo ""
echo "=== Native binaries (c / cpp / go / rust) ==="
while IFS= read -r bin; do
  lang=$(basename "$(dirname "$bin")")
  algo=$(basename "$(dirname "$(dirname "$bin")")")
  cat=$(basename  "$(dirname "$(dirname "$(dirname "$bin")")")")
  run_suite "$bin" "$cat" "$algo" "$lang" "$(realpath "$bin")"
done < <(find benchmarks -type f -name benchmark | sort)

echo ""
echo "=== Java ==="
while IFS= read -r cls; do
  d=$(dirname "$cls")
  algo=$(basename "$(dirname "$d")")
  cat=$(basename  "$(dirname "$(dirname "$d")")")
  run_suite "$d" "$cat" "$algo" "java" \
      java -XX:+UseSerialGC -cp "$(realpath "$d")" Main
done < <(find benchmarks -type f -name Main.class | sort)

cleanup

echo ""
echo "=== Integrating ==="
python3 scripts/integrate_energy.py \
    --samples "$SAMPLES_CSV" \
    --runs    "$RUNS_CSV" \
    --idle    "$IDLE_FILE" \
    --out     results/raw/arm_results.csv

echo ""
echo "Done. Idle baseline used: ${IDLE_POWER_W} W"
echo "Raw sample stream retained at ${SAMPLES_CSV} (keep it -- it is the"
echo "auditable evidence that integration actually happened)."
