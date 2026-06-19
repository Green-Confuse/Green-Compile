"""
aggregate_arm.py  —  NEW (ARM equivalent of fixed aggregate.py)
===============================================================
Run this on the ARM machine (Raspberry Pi 5) after run_all_arm.sh completes.
Copy the two output CSVs to the AMD machine's results/processed/ directory
before running compute_metrics.py so global normalisation includes both platforms.

Usage:  python scripts/aggregate_arm.py
Inputs: results/raw/arm_results.csv
Outputs:
  results/processed/arm_avg.csv         — mean ± std per benchmark
  results/processed/arm_results_ok.csv  — raw per-run data for stats
"""

import pandas as pd
import numpy as np

df = pd.read_csv("results/raw/arm_results.csv")
ok = df[df["status"] == "OK"].copy()

print(f"Total runs : {len(df)}")
print(f"OK runs    : {len(ok)}")
print(f"FAIL runs  : {len(df) - len(ok)}")

ok.to_csv("results/processed/arm_results_ok.csv", index=False)
print("Saved: results/processed/arm_results_ok.csv")

g = ok.groupby(["category", "algorithm", "language"], as_index=False).agg(
    time_s       =("time_s",   "mean"),
    energy_j     =("energy_j", "mean"),
    power_w      =("power_w",  "mean"),
    std_time_s   =("time_s",   "std"),
    std_energy_j =("energy_j", "std"),
    std_power_w  =("power_w",  "std"),
    n_runs       =("time_s",   "count"),
)

g["sem_time_s"]   = g["std_time_s"]   / np.sqrt(g["n_runs"])
g["sem_energy_j"] = g["std_energy_j"] / np.sqrt(g["n_runs"])
g["sem_power_w"]  = g["std_power_w"]  / np.sqrt(g["n_runs"])
g["cv_time_pct"]  = (g["std_time_s"]  / g["time_s"])   * 100
g["cv_energy_pct"]= (g["std_energy_j"]/ g["energy_j"]) * 100

g.to_csv("results/processed/arm_avg.csv", index=False)
print("Saved: results/processed/arm_avg.csv")

noisy = g[g["cv_energy_pct"] > 10].sort_values("cv_energy_pct", ascending=False)
if not noisy.empty:
    print("\n⚠  High-variance benchmarks (CV > 10% on energy):")
    print(noisy[["category", "algorithm", "language", "cv_energy_pct"]].to_string(index=False))
