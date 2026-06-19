#!/usr/bin/env bash
# run_experiments.sh — AMD primary machine (3-platform aware)
# ============================================================
# This machine is the PRIMARY analysis node. It:
#   1. Runs the AMD benchmarks
#   2. Waits for arm_avg.csv and intel_avg.csv to be copied in
#   3. Runs compute_metrics.py across all available platforms
#
# USAGE:
#   AMD-only (no other platforms ready yet):
#     bash scripts/run_experiments.sh
#
#   All 3 platforms (after copying arm_avg.csv + intel_avg.csv):
#     SKIP_RUN=1 bash scripts/run_experiments.sh
#     (skips the benchmark run, just re-runs analysis)

if [ -f "$HOME/Desktop/myenv/bin/activate" ]; then
  source "$HOME/Desktop/myenv/bin/activate"
fi

set -e
export PATH="$HOME/.cargo/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

SKIP_RUN="${SKIP_RUN:-0}"

if [[ "$SKIP_RUN" != "1" ]]; then
  echo "=== GREENCOMPILE AMD EXPERIMENT START ==="
  echo "  Optimisation : C/C++ -O2, Rust -C opt-level=3"
  echo "  Java warmup  : 30 runs"
  echo "  Idle baseline: measured before benchmarks start"
  echo ""

  sudo -v
  bash "$SCRIPT_DIR/env_check.sh"
  bash "$SCRIPT_DIR/prepare_env.sh"
  bash "$SCRIPT_DIR/build_all.sh"
  bash "$SCRIPT_DIR/run_all_amd.sh"
  python3 "$SCRIPT_DIR/aggregate.py"
  bash "$SCRIPT_DIR/restore_env.sh"
fi

# ── Check which platform CSVs are present ────────────────────────────────────
echo ""
echo "=== Platform data status ==="
for platform in amd arm intel; do
  if [ -f "results/processed/${platform}_avg.csv" ]; then
    rows=$(tail -n +2 "results/processed/${platform}_avg.csv" | wc -l)
    echo "  ✅ ${platform}_avg.csv  ($rows rows)"
  else
    echo "  ⏳ ${platform}_avg.csv  NOT YET AVAILABLE"
  fi
done
echo ""

# ── Run global analysis with whatever platforms are present ──────────────────
python3 "$SCRIPT_DIR/compute_metrics.py"

echo ""
echo "=== COMPLETE ==="
echo ""
echo "If ARM or Intel data is still missing, copy:"
echo "  arm_avg.csv + arm_results_ok.csv     from Raspberry Pi 5"
echo "  intel_avg.csv + intel_results_ok.csv  from Intel machine"
echo "into results/processed/, then run:"
echo "  SKIP_RUN=1 bash scripts/run_experiments.sh"
