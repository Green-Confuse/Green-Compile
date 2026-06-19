#!/usr/bin/env bash
# run_experiments.sh — Intel platform full pipeline
set -e
export PATH="$HOME/.cargo/bin:$PATH"

if [ -f "$HOME/Desktop/myenv/bin/activate" ]; then source "$HOME/Desktop/myenv/bin/activate"; fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== GREENCOMPILE INTEL EXPERIMENT START ==="
echo "  Energy path  : /sys/class/powercap/intel-rapl:0/energy_uj"
echo "  Optimisation : C/C++ -O2, Rust -C opt-level=3"
echo "  Java warmup  : 30 runs"
echo ""

sudo -v
bash "$SCRIPT_DIR/env_check.sh"
bash "$SCRIPT_DIR/prepare_env.sh"
bash "$SCRIPT_DIR/build_all.sh"
bash "$SCRIPT_DIR/run_all_intel.sh"
python3 "$SCRIPT_DIR/aggregate_intel.py"
bash "$SCRIPT_DIR/restore_env.sh"

echo ""
echo "=== INTEL EXPERIMENT COMPLETE ==="
echo "Files to copy to the primary analysis machine:"
echo "  results/processed/intel_avg.csv"
echo "  results/processed/intel_results_ok.csv"
