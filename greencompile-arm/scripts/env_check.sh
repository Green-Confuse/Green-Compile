#!/usr/bin/env bash
# env_check.sh — Raspberry Pi 5 environment check
set -e
export PATH="$HOME/.cargo/bin:/usr/local/go/bin:$PATH"

echo "=== Environment Check (Raspberry Pi 5) ==="

echo "[OS]"
cat /etc/os-release | grep PRETTY_NAME

echo "[CPU]"
lscpu | grep "Model name"

echo "[Compilers]"
gcc --version   | head -1
g++ --version   | head -1
javac --version
rustc --version
go version

echo "[PMIC Power Sensor]"
if vcgencmd pmic_read_adc >/dev/null 2>&1; then
    WATTS=$(python3 scripts/measure_power.py)
    echo "vcgencmd pmic_read_adc OK  (current total: ${WATTS} W)"
else
    echo "ERROR: vcgencmd not working"
    exit 1
fi

echo "[CPU Governor]"
GOV=$(cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor 2>/dev/null || echo "unknown")
echo "Governor: $GOV"
[[ "$GOV" != "performance" ]] && echo "  (will be set to performance by prepare_env.sh)"

echo "=== Environment OK ==="
