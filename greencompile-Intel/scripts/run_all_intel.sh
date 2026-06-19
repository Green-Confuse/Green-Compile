#!/usr/bin/env bash
# run_all_intel.sh — Intel platform measurement harness
# ======================================================
# Identical to run_all_amd.sh except:
#   - Output: results/raw/intel_results.csv  (→ aggregate_intel.py → intel_avg.csv)
#   - ENERGY_PATH: same /sys/class/powercap/intel-rapl:0/energy_uj
#     (Intel and AMD both use this RAPL sysfs path on Linux)
#   - DOMAIN_NAME: "intel-rapl:0"

set -u

OUT="results/raw/intel_results.csv"
mkdir -p results/raw results/processed
echo "category,algorithm,language,run,status,time_s,energy_j,dynamic_energy_j,power_w,idle_power_w,domain,energy_path,exit_code" > "$OUT"

sudo -v

ENERGY_PATH="/sys/class/powercap/intel-rapl:0/energy_uj"
DOMAIN_NAME=$(sudo cat /sys/class/powercap/intel-rapl:0/name 2>/dev/null || echo "intel-rapl:0")

echo "Measuring idle power baseline (10 seconds)..."
IDLE_E1=$(sudo cat "$ENERGY_PATH")
sleep 10
IDLE_E2=$(sudo cat "$ENERGY_PATH")
IDLE_POWER_W=$(python3 - <<PY
e1=$IDLE_E1; e2=$IDLE_E2
joules = (e2 - e1) / 1e6
print(round(joules / 10.0, 4))
PY
)
echo "Idle power: ${IDLE_POWER_W} W"
echo "$IDLE_POWER_W" > results/processed/idle_power_w.txt

JAVA_WARMUP_RUNS=30
NOJAVA_WARMUP_RUNS=3

source config/inputs.sh

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

  ej=$(python3 - <<PY
print(round($euj / 1e6, 9))
PY
)
  dyn_ej=$(python3 - <<PY
total = $euj / 1e6
idle_correction = float("$IDLE_POWER_W") * float("$t_s")
print(round(max(0.0, total - idle_correction), 9))
PY
)
  pw=$(python3 - <<PY
ej = float("$ej"); ts = float("$t_s")
print(round(ej / ts, 6) if ts > 0 else 0.0)
PY
)
  short=$(python3 - <<PY
print("WARN_SHORT" if float("$t_s") < 0.050 else "")
PY
)
  [[ -n "$short" ]] && echo "  ⚠  ${algo}/${lang} run${run}: ${t_s}s < 50ms" >&2

  if [[ $rc -eq 0 ]]; then
    echo "$cat,$algo,$lang,$run,OK,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN_NAME,$ENERGY_PATH,$rc" >> "$OUT"
  else
    echo "$cat,$algo,$lang,$run,FAIL,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN_NAME,$ENERGY_PATH,$rc" >> "$OUT"
  fi
}

# ── Non-Java ──────────────────────────────────────────────────────────────────
while IFS= read -r bin; do
  lang=$(basename "$(dirname "$bin")")
  algo=$(basename "$(dirname "$(dirname "$bin")")")
  cat=$(basename "$(dirname "$(dirname "$(dirname "$bin")")")")
  cmd=$(get_cmd "$cat" "$algo" "$lang" "$bin")
  echo "Warming up ${algo}/${lang} (${NOJAVA_WARMUP_RUNS} runs)..."
  for _ in $(seq 1 $NOJAVA_WARMUP_RUNS); do bash -c "$cmd" >/dev/null 2>/dev/null || true; done
  for r in {1..10}; do measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"; done
done < <(find benchmarks -type f -name benchmark)

# ── Java ──────────────────────────────────────────────────────────────────────
while IFS= read -r cls; do
  d=$(dirname "$cls")
  lang="java"
  algo=$(basename "$(dirname "$d")")
  cat=$(basename "$(dirname "$(dirname "$d")")")
  cmd=$(get_cmd "$cat" "$algo" "$lang" "$d")
  echo "Warming up ${algo}/java (${JAVA_WARMUP_RUNS} runs)..."
  for _ in $(seq 1 $JAVA_WARMUP_RUNS); do bash -c "$cmd" >/dev/null 2>/dev/null || true; done
  for r in {1..10}; do measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"; done
done < <(find benchmarks -type f -name Main.class)

echo ""
echo "✅ Saved: $OUT  (idle: ${IDLE_POWER_W} W)"
