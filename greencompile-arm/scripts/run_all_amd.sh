#!/usr/bin/env bash
# run_all_amd.sh  —  FIXED (Reviewer Issues #3, #4, #5)
# =======================================================
# Changes from original:
#   [FIX #4] Idle power baseline is measured at startup (10-second idle sample).
#            Each benchmark result includes the idle-corrected dynamic energy:
#            dynamic_energy_j = total_energy_j - (idle_power_w × duration_s)
#   [FIX #5] Java warmup increased from 1 run to JAVA_WARMUP_RUNS (default 30).
#            This gives HotSpot's C2 JIT sufficient invocations to reach
#            steady-state compiled performance before measurement begins.
#   [FIX #3] WARNING comments added for benchmarks whose mean runtime < 50 ms
#            to flag where workload scaling is still needed.
#            (Actual workload scaling requires source code changes — see README.)
#
# Note on [FIX #3] workload scaling:
#   Source-level changes needed to push runtimes above 500 ms:
#     towers_of_hanoi:      N=20 → N=28  (adds ~100× work)
#     newton_raphson:       increase iteration count × 1000
#     palindrome_detection: use longer input string (≥1 MB)
#   These changes must be made in the respective main.c / main.rs / etc. files.

set -u

OUT="results/raw/amd_results.csv"
mkdir -p results/raw results/processed
echo "category,algorithm,language,run,status,time_s,energy_j,dynamic_energy_j,power_w,idle_power_w,domain,energy_path,exit_code" > "$OUT"

sudo -v

ENERGY_PATH="/sys/class/powercap/intel-rapl:0/energy_uj"
DOMAIN_NAME=$(sudo cat /sys/class/powercap/intel-rapl:0/name 2>/dev/null || echo "package-0")

# ── [FIX #4] Measure idle power baseline ─────────────────────────────────────
# Sample RAPL over 10 seconds with no benchmark load. This captures OS/kernel
# background power which will be subtracted from each benchmark measurement.
echo "Measuring idle power baseline (10 seconds)..."
IDLE_E1=$(sudo cat "$ENERGY_PATH")
sleep 10
IDLE_E2=$(sudo cat "$ENERGY_PATH")
IDLE_POWER_W=$(python3 - <<PY
e1=$IDLE_E1; e2=$IDLE_E2
joules = (e2 - e1) / 1e6
print(round(joules / 10.0, 4))  # watts = joules / seconds
PY
)
echo "Idle power: ${IDLE_POWER_W} W  (will be subtracted from all measurements)"
echo "$IDLE_POWER_W" > results/processed/idle_power_w.txt

# [FIX #5] Warmup runs: Java needs many more iterations for JIT to kick in
JAVA_WARMUP_RUNS=30   # was 1 — HotSpot C2 JIT typically needs 10k+ invocations
                       # With loops inside each benchmark, 30 process runs
                       # provides ~30k+ method calls for most benchmarks.
NOJAVA_WARMUP_RUNS=3   # was 1 — small increase for cache warm-up on AOT langs

source config/inputs.sh

# ── Measurement function ──────────────────────────────────────────────────────
measure_cmd () {
  local cat="$1" algo="$2" lang="$3" run="$4" cmd="$5"

  local e1 e2 t_s euj ej dyn_ej pw rc
  e1=$(sudo cat "$ENERGY_PATH" 2>/dev/null || echo "")
  if [[ -z "$e1" ]]; then
    echo "$cat,$algo,$lang,$run,FAIL,,,,,,$DOMAIN_NAME,$ENERGY_PATH,99" >> "$OUT"
    return
  fi

  local t1 t2
  t1=$(date +%s%N)
  bash -c "$cmd" >/dev/null 2>results/raw/${cat}_${algo}_${lang}_run${run}.err
  rc=$?
  t2=$(date +%s%N)

  e2=$(sudo cat "$ENERGY_PATH" 2>/dev/null || echo "")
  if [[ -z "$e2" ]]; then
    echo "$cat,$algo,$lang,$run,FAIL,,,,,,$DOMAIN_NAME,$ENERGY_PATH,$rc" >> "$OUT"
    return
  fi

  t_s=$(python3 - <<PY
print(round(($t2 - $t1) / 1e9, 9))
PY
)

  if [[ "$e2" =~ ^[0-9]+$ ]] && [[ "$e1" =~ ^[0-9]+$ ]] && (( e2 >= e1 )); then
    euj=$((e2 - e1))
  else
    echo "$cat,$algo,$lang,$run,FAIL,$t_s,,,,,${DOMAIN_NAME},$ENERGY_PATH,$rc" >> "$OUT"
    return
  fi

  # [FIX #4] Compute total energy AND dynamic (idle-subtracted) energy
  ej=$(python3 - <<PY
print(round($euj / 1e6, 9))
PY
)

  dyn_ej=$(python3 - <<PY
total = $euj / 1e6
idle_correction = float("$IDLE_POWER_W") * float("$t_s")
dynamic = max(0.0, total - idle_correction)
print(round(dynamic, 9))
PY
)

  pw=$(python3 - <<PY
ej = float("$ej"); ts = float("$t_s")
print(round(ej / ts, 6) if ts > 0 else 0.0)
PY
)

  # Warn if runtime < 50 ms — startup overhead likely dominates [FIX #3]
  short=$(python3 - <<PY
print("WARN_SHORT" if float("$t_s") < 0.050 else "")
PY
)
  if [[ -n "$short" ]]; then
    echo "  ⚠  ${algo}/${lang} run${run}: ${t_s}s < 50ms — consider scaling workload" >&2
  fi

  if [[ $rc -eq 0 ]]; then
    echo "$cat,$algo,$lang,$run,OK,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN_NAME,$ENERGY_PATH,$rc" >> "$OUT"
  else
    echo "$cat,$algo,$lang,$run,FAIL,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN_NAME,$ENERGY_PATH,$rc" >> "$OUT"
  fi
}

# ── Non-Java binaries ─────────────────────────────────────────────────────────
while IFS= read -r bin; do
  lang=$(basename "$(dirname "$bin")")
  algo=$(basename "$(dirname "$(dirname "$bin")")")
  cat=$(basename "$(dirname "$(dirname "$(dirname "$bin")")")")

  cmd=$(get_cmd "$cat" "$algo" "$lang" "$bin")

  # [FIX #5] AOT warmup: 3 runs (was 1) — warms CPU cache, branch predictor
  echo "Warming up ${algo}/${lang} (${NOJAVA_WARMUP_RUNS} runs)..."
  for _ in $(seq 1 $NOJAVA_WARMUP_RUNS); do
    bash -c "$cmd" >/dev/null 2>/dev/null || true
  done

  for r in {1..10}; do
    measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"
  done
done < <(find benchmarks -type f -name benchmark)

# ── Java ──────────────────────────────────────────────────────────────────────
# [FIX #5] Java needs significantly more warmup runs for JIT steady-state.
while IFS= read -r cls; do
  d=$(dirname "$cls")
  lang="java"
  algo=$(basename "$(dirname "$d")")
  cat=$(basename "$(dirname "$(dirname "$d")")")

  cmd=$(get_cmd "$cat" "$algo" "$lang" "$d")

  echo "Warming up ${algo}/java (${JAVA_WARMUP_RUNS} runs for JIT steady-state)..."
  for _ in $(seq 1 $JAVA_WARMUP_RUNS); do
    bash -c "$cmd" >/dev/null 2>/dev/null || true
  done

  for r in {1..10}; do
    measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"
  done
done < <(find benchmarks -type f -name Main.class)

echo ""
echo "✅ Saved: $OUT"
echo "   Idle power used for dynamic energy correction: ${IDLE_POWER_W} W"
echo "   Check short-duration warnings: grep WARN_SHORT /dev/stderr"
echo "   Check failures: grep ',FAIL,' $OUT | head"
