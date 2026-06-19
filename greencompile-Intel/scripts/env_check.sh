#!/usr/bin/env bash
# env_check.sh — Intel platform environment check
# (Intel i5/i7/i9 — uses same RAPL path as AMD)
set -e
export PATH="$HOME/.cargo/bin:$PATH"

echo "=== Environment Check (Intel) ==="

echo "[OS]"
lsb_release -a 2>/dev/null | grep -E "Description|Release"

echo "[CPU]"
lscpu | grep "Model name"

echo "[Compilers]"
gcc   --version | head -n 1
g++   --version | head -n 1
javac --version
rustc --version
go version

echo "[Energy Counter]"
# Intel and AMD both expose RAPL through the same sysfs path
sudo cat /sys/class/powercap/intel-rapl:0/energy_uj >/dev/null
echo "energy_uj OK (intel-rapl:0)"

echo "[Governor]"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo "=== Environment OK ==="
