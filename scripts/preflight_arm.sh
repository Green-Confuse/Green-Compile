#!/usr/bin/env bash
# preflight_arm.sh — verify the Raspberry Pi 5 is fit to measure on.
# Run this BEFORE run_all_arm.sh. Every FAIL must be resolved; WARN should be
# recorded in the paper's experimental-setup section.

set -u
PASS=0; WARN=0; FAIL=0
ok()   { echo "  [ OK ]  $*"; PASS=$((PASS+1)); }
warn() { echo "  [WARN]  $*"; WARN=$((WARN+1)); }
bad()  { echo "  [FAIL]  $*"; FAIL=$((FAIL+1)); }

echo "=============================================================="
echo " GreenCompile preflight — Raspberry Pi 5"
echo " $(date -Is)"
echo "=============================================================="

echo ""
echo "--- Hardware / OS ---"
MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo unknown)
echo "  model   : $MODEL"
echo "  kernel  : $(uname -r)  ($(uname -m))"
echo "  os      : $(. /etc/os-release && echo "$PRETTY_NAME")"
echo "  memory  : $(awk '/MemTotal/{printf "%.1f GB", $2/1048576}' /proc/meminfo)"
case "$MODEL" in *"Raspberry Pi 5"*) ok "Raspberry Pi 5 detected";;
                 *) bad "Not a Pi 5 — PMIC rail names will differ";; esac

echo ""
echo "--- Throttling / power supply ---"
TH=$(vcgencmd get_throttled 2>/dev/null || echo "throttled=ERR")
echo "  $TH"
TV=${TH#throttled=}
if [[ "$TV" == "0x0" ]]; then ok "no throttling and no past throttling events"
else
  bad "throttled flags set ($TV)"
  echo "         bit 0  under-voltage now       bit 16 under-voltage occurred"
  echo "         bit 1  freq capped now         bit 17 freq cap occurred"
  echo "         bit 2  throttled now           bit 18 throttling occurred"
  echo "         bit 3  soft temp limit now     bit 19 soft temp limit occurred"
  echo "         Use the official 27 W USB-C PSU. Clear history by rebooting."
fi

echo ""
echo "--- Thermal ---"
T=$(awk '{printf "%.1f", $1/1000}' /sys/class/thermal/thermal_zone0/temp)
echo "  SoC temperature: ${T} C"
awk -v t="$T" 'BEGIN{exit !(t<60)}' && ok "idle temp under 60 C" \
    || warn "idle temp ${T} C — needs an active cooler for sustained runs"
FAN=$(find /sys/class/hwmon -name 'pwm1' 2>/dev/null | head -1)
[[ -n "$FAN" ]] && ok "fan control present ($FAN)" \
                || warn "no PWM fan detected — official Active Cooler strongly advised"

echo ""
echo "--- CPU frequency policy ---"
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)
CUR=$(vcgencmd measure_clock arm | cut -d= -f2)
echo "  governor: $GOV     arm clock: $((CUR/1000000)) MHz"
[[ "$GOV" == "performance" ]] && ok "governor = performance" \
    || bad "governor is '$GOV' — set it: sudo cpufreq-set -r -g performance
              (or: echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor)"

echo ""
echo "--- PMIC sampling cost (this determines your minimum workload size) ---"
python3 - <<'PY'
import subprocess, time, statistics as st, sys
ts = []
for _ in range(30):
    t = time.perf_counter()
    subprocess.run(["vcgencmd", "pmic_read_adc"], capture_output=True)
    ts.append((time.perf_counter() - t) * 1000)
med = st.median(ts)
print(f"  vcgencmd pmic_read_adc: median {med:.1f} ms  "
      f"(min {min(ts):.1f}, max {max(ts):.1f})")
rate = 1000.0 / med
print(f"  => maximum achievable sampling rate ~{rate:.0f} Hz")
for target in (20, 50, 200):
    print(f"     for {target:3d} samples/run, each run must last "
          f">= {target/rate:.2f} s")
print()
if med > 40:
    print("  [WARN]  vcgencmd is slow on this system; aim for >= 10 s runs.")
else:
    print("  [ OK ]  sampling cost acceptable; 5 s runs give ample samples.")
PY

echo ""
echo "--- PMIC rails ---"
python3 - <<'PY'
import re, subprocess
out = subprocess.run(["vcgencmd","pmic_read_adc"],capture_output=True,text=True).stdout
cur = dict(re.findall(r"\s*(\S+)_A\s+current\(\d+\)=([0-9.]+)A", out))
vol = dict(re.findall(r"\s*(\S+)_V\s+volt\(\d+\)=([0-9.]+)V", out))
paired = sorted(set(cur) & set(vol))
tot = sum(float(cur[k])*float(vol[k]) for k in paired)
print(f"  {len(paired)} paired rails: {', '.join(paired)}")
print(f"  total board power right now: {tot:.4f} W")
print("  [ OK ]" if len(paired) >= 5 else "  [WARN] few rails paired")
PY

echo ""
echo "--- Toolchains ---"
for t in "gcc --version" "g++ --version" "rustc --version" "go version" "java -version" "javac -version"; do
  n=${t%% *}
  if command -v "$n" >/dev/null 2>&1; then
    v=$($t 2>&1 | head -1)
    ok "$v"
  else
    bad "$n not installed"
  fi
done

echo ""
echo "--- Background load ---"
LOAD=$(awk '{print $1}' /proc/loadavg)
echo "  1-min load average: $LOAD"
awk -v l="$LOAD" 'BEGIN{exit !(l<0.30)}' && ok "system is quiet" \
    || warn "load $LOAD — stop background services before measuring"
if systemctl is-active --quiet bluetooth 2>/dev/null; then
  warn "bluetooth is running — sudo systemctl stop bluetooth"
else ok "bluetooth inactive"; fi
if [[ -n "$(pgrep -x 'gnome-shell|Xorg|wayfire|labwc' 2>/dev/null)" ]]; then
  warn "a desktop session is running — measure from a console/SSH with the
              desktop stopped (sudo systemctl set-default multi-user.target)"
else ok "no desktop session detected"; fi

echo ""
echo "=============================================================="
printf " PASS %d   WARN %d   FAIL %d\n" "$PASS" "$WARN" "$FAIL"
[[ $FAIL -gt 0 ]] && echo " Resolve every FAIL before running the experiment." \
                  || echo " Preflight clear — proceed to calibration."
echo "=============================================================="
exit $(( FAIL > 0 ))
