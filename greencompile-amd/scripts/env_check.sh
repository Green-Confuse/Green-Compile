#!/usr/bin/env bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"


echo "=== Environment Check ==="

echo "[OS]"
lsb_release -a | head -n 3

echo "[CPU]"
lscpu | grep "Model name"

echo "[Compilers]"
gcc --version | head -n 1
g++ --version | head -n 1
javac --version
rustc --version
go version

echo "[Energy Counter]"
sudo cat /sys/class/powercap/intel-rapl:0/energy_uj >/dev/null
echo "energy_uj OK"

echo "[Governor]"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo "=== Environment OK ==="
