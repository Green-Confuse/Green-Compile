"""
aggregate.py  —  FIXED (Reviewer Issues #9, #10)
=================================================
Changes from original:
  [FIX #10] Added std_time_s, std_energy_j, std_power_w, sem_* columns
             alongside mean values so Tables 9-11 can show ± variability.
  [FIX #10] Added n_runs column so readers see exactly how many OK runs
             contributed to each mean (may be < 10 if some FAILed).
  [FIX #9]  Raw per-run data is preserved in amd_results_ok.csv so that
             compute_metrics.py can perform statistical tests on individual
             observations rather than collapsed means.

Usage (unchanged):  python scripts/aggregate.py
Inputs:             results/raw/amd_results.csv
Outputs:
  results/processed/amd_avg.csv          — mean + std (replaces old file)
  results/processed/amd_results_ok.csv   — NEW: filtered raw runs for stats
"""

import pandas as pd
import numpy as np

# ── Load raw results ─────────────────────────────────────────────────────────
df = pd.read_csv("results/raw/amd_results.csv")

# Keep only successful runs
ok = df[df["status"] == "OK"].copy()

print(f"Total runs : {len(df)}")
print(f"OK runs    : {len(ok)}")
print(f"FAIL runs  : {len(df) - len(ok)}")

# ── [FIX #9] Save filtered raw data for statistical tests ────────────────────
ok.to_csv("results/processed/amd_results_ok.csv", index=False)
print("Saved: results/processed/amd_results_ok.csv  (raw per-run data for stats)")

# ── [FIX #10] Aggregate: mean + std + sem + count ────────────────────────────
g = ok.groupby(["category", "algorithm", "language"], as_index=False).agg(
    time_s    =("time_s",   "mean"),
    energy_j  =("energy_j", "mean"),
    power_w   =("power_w",  "mean"),
    # NEW: variability columns
    std_time_s   =("time_s",   "std"),
    std_energy_j =("energy_j", "std"),
    std_power_w  =("power_w",  "std"),
    n_runs       =("time_s",   "count"),
)

# Standard error of the mean  (std / sqrt(n))
g["sem_time_s"]   = g["std_time_s"]   / np.sqrt(g["n_runs"])
g["sem_energy_j"] = g["std_energy_j"] / np.sqrt(g["n_runs"])
g["sem_power_w"]  = g["std_power_w"]  / np.sqrt(g["n_runs"])

# Coefficient of variation (%) — useful for spotting noisy benchmarks
g["cv_time_pct"]   = (g["std_time_s"]   / g["time_s"])   * 100
g["cv_energy_pct"] = (g["std_energy_j"] / g["energy_j"]) * 100

g.to_csv("results/processed/amd_avg.csv", index=False)
print("Saved: results/processed/amd_avg.csv  (mean ± std per benchmark-language)")

# ── Sanity report ─────────────────────────────────────────────────────────────
noisy = g[g["cv_energy_pct"] > 10].sort_values("cv_energy_pct", ascending=False)
if not noisy.empty:
    print("\n⚠  High-variance benchmarks (CV > 10% on energy):")
    print(noisy[["category", "algorithm", "language", "cv_energy_pct"]].to_string(index=False))
