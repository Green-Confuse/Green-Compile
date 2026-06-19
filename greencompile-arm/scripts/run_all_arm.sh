#!/usr/bin/env bash
# run_all_arm.sh — Raspberry Pi 5 measurement harness (PMIC via vcgencmd)
# ==========================================================================
# Energy measurement method:
#   - Reads instantaneous total board power (W) via vcgencmd pmic_read_adc
#   - power is sampled BEFORE and AFTER each benchmark run
#   - energy_j = ((P_before + P_after) / 2) × duration_s   [trapezoidal rule]
#   - dynamic_energy_j = energy_j - (idle_power_w × duration_s)
#
# This is equivalent to what RAPL does on x86, just at board level.
# All values saved to results/raw/arm_results.csv

set -u

OUT="results/raw/arm_results.csv"
mkdir -p results/raw results/processed
echo "category,algorithm,language,run,status,time_s,energy_j,dynamic_energy_j,power_w,idle_power_w,domain,energy_path,exit_code" > "$OUT"

DOMAIN="vcgencmd_pmic"
ENERGY_PATH="vcgencmd pmic_read_adc"
MEASURE_PY="scripts/measure_power.py"

# ── Verify vcgencmd works ─────────────────────────────────────────────────────
if ! vcgencmd pmic_read_adc >/dev/null 2>&1; then
    echo "ERROR: vcgencmd pmic_read_adc failed."
    echo "Make sure you are running on a Raspberry Pi 5."
    exit 1
fi
echo "✅ PMIC power measurement via vcgencmd: OK"

# ── Idle power baseline (10 seconds, 10 samples) ─────────────────────────────
echo "Measuring idle power baseline (10 seconds)..."
IDLE_READINGS=()
for i in $(seq 1 10); do
    v=$(python3 "$MEASURE_PY")
    IDLE_READINGS+=("$v")
    sleep 1
done

IDLE_POWER_W=$(python3 -c "
vals=[${IDLE_READINGS[*]}]
print(round(sum(vals)/len(vals), 4))
")
echo "Idle power: ${IDLE_POWER_W} W"
echo "$IDLE_POWER_W" > results/processed/idle_power_w.txt

JAVA_WARMUP_RUNS=30
NOJAVA_WARMUP_RUNS=3

source config/inputs.sh

# ── Measurement function ──────────────────────────────────────────────────────
measure_cmd () {
    local cat="$1" algo="$2" lang="$3" run="$4" cmd="$5"
    local p1 p2 t1 t2 t_s ej dyn_ej pw rc

    # Power sample BEFORE benchmark
    p1=$(python3 "$MEASURE_PY")
    if [[ -z "$p1" ]] || [[ "$p1" == "0.0" ]]; then
        echo "$cat,$algo,$lang,$run,FAIL,,,,,,$DOMAIN,$ENERGY_PATH,99" >> "$OUT"
        return
    fi

    t1=$(date +%s%N)
    bash -c "$cmd" >/dev/null 2>results/raw/${cat}_${algo}_${lang}_run${run}.err
    rc=$?
    t2=$(date +%s%N)

    # Power sample AFTER benchmark
    p2=$(python3 "$MEASURE_PY")
    [[ -z "$p2" ]] && p2="$p1"

    t_s=$(python3 -c "print(round(($t2-$t1)/1e9, 9))")

    # Energy = trapezoidal average power × duration
    ej=$(python3 -c "
p1=float('$p1'); p2=float('$p2'); ts=float('$t_s')
energy = ((p1+p2)/2.0) * ts
print(round(energy, 9))
")

    # Dynamic energy (idle-corrected)
    dyn_ej=$(python3 -c "
ej=float('$ej'); idle=float('$IDLE_POWER_W'); ts=float('$t_s')
print(round(max(0.0, ej - idle*ts), 9))
")

    pw=$(python3 -c "
ej=float('$ej'); ts=float('$t_s')
print(round(ej/ts, 6) if ts>0 else 0.0)
")

    # Warn if benchmark ran too short
    short=$(python3 -c "print('WARN' if float('$t_s')<0.050 else '')")
    [[ -n "$short" ]] && echo "  ⚠  ${algo}/${lang} run${run}: ${t_s}s < 50ms" >&2

    if [[ $rc -eq 0 ]]; then
        echo "$cat,$algo,$lang,$run,OK,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN,$ENERGY_PATH,$rc" >> "$OUT"
    else
        echo "$cat,$algo,$lang,$run,FAIL,$t_s,$ej,$dyn_ej,$pw,$IDLE_POWER_W,$DOMAIN,$ENERGY_PATH,$rc" >> "$OUT"
    fi
}

# ── Non-Java binaries ─────────────────────────────────────────────────────────
while IFS= read -r bin; do
    lang=$(basename "$(dirname "$bin")")
    algo=$(basename "$(dirname "$(dirname "$bin")")")
    cat=$(basename "$(dirname "$(dirname "$(dirname "$bin")")")")
    cmd=$(get_cmd "$cat" "$algo" "$lang" "$bin")

    echo "Warming up ${algo}/${lang} (${NOJAVA_WARMUP_RUNS} runs)..."
    for _ in $(seq 1 $NOJAVA_WARMUP_RUNS); do
        bash -c "$cmd" >/dev/null 2>/dev/null || true
    done
    for r in {1..10}; do
        measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"
    done
done < <(find benchmarks -type f -name benchmark)

# ── Java ──────────────────────────────────────────────────────────────────────
while IFS= read -r cls; do
    d=$(dirname "$cls"); lang="java"
    algo=$(basename "$(dirname "$d")")
    cat=$(basename "$(dirname "$(dirname "$d")")")
    cmd=$(get_cmd "$cat" "$algo" "$lang" "$d")

    echo "Warming up ${algo}/java (${JAVA_WARMUP_RUNS} JIT warmup runs)..."
    for _ in $(seq 1 $JAVA_WARMUP_RUNS); do
        bash -c "$cmd" >/dev/null 2>/dev/null || true
    done
    for r in {1..10}; do
        measure_cmd "$cat" "$algo" "$lang" "$r" "$cmd"
    done
done < <(find benchmarks -type f -name Main.class)

echo ""
echo "✅ Saved: $OUT"
echo "   Idle: ${IDLE_POWER_W} W  |  Method: PMIC (vcgencmd)"
echo "   Failures: $(grep -c ',FAIL,' "$OUT" || echo 0)"
