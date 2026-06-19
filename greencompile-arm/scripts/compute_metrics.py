"""
compute_metrics.py — 3-Platform Version (AMD + ARM + Intel)
============================================================
Run on the PRIMARY analysis machine after collecting:
  results/processed/amd_avg.csv      (from AMD machine)
  results/processed/arm_avg.csv      (from RPi5, copy over)
  results/processed/intel_avg.csv    (from Intel machine, copy over)

All three CSVs are pooled before normalisation so GES values are
globally comparable across all platforms and languages.

Fixes applied:
  [FIX #1]  Global normalisation across ALL platforms
  [FIX #7]  EDP removed from GES (collinearity)
  [FIX #9]  Kruskal-Wallis + Dunn post-hoc per platform
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import kruskal

try:
    import scikit_posthocs as sp
    POSTHOC_AVAILABLE = True
except ImportError:
    print("⚠  scikit-posthocs not installed — Dunn tests will be skipped.")
    POSTHOC_AVAILABLE = False

W_ENERGY = 0.50
W_TIME   = 0.50

def minmax_global(s):
    lo, hi = s.min(), s.max()
    return pd.Series(0.0, index=s.index) if hi == lo else (s - lo) / (hi - lo)

def minmax_local(s):
    lo, hi = s.min(), s.max()
    return pd.Series(0.0, index=s.index) if hi == lo else (s - lo) / (hi - lo)

def add_derived(df):
    df = df.copy()
    df["edp"] = df["energy_j"] * df["time_s"]
    df["aei"] = 1.0 / (df["energy_j"] * df["time_s"])
    return df

def add_rankings(df, ges_col="ges"):
    df = df.copy()
    df["rank_in_category"]  = df.groupby("category") [ges_col].rank(method="min", ascending=True)
    df["rank_in_algorithm"] = df.groupby("algorithm")[ges_col].rank(method="min", ascending=True)
    df["rank_in_cat_algo"]  = df.groupby(["category","algorithm"])[ges_col].rank(method="min", ascending=True)
    return df

# ── Load available platforms ───────────────────────────────────────────────────
platforms = {}
for platform in ("amd", "arm", "intel"):
    path = f"results/processed/{platform}_avg.csv"
    if os.path.exists(path):
        pf = pd.read_csv(path)
        pf["platform"] = platform
        pf = add_derived(pf)
        platforms[platform] = pf
        print(f"Loaded {path}  ({len(pf)} rows)")
    else:
        print(f"ℹ  {path} not found — skipping {platform.upper()}.")

if not platforms:
    raise FileNotFoundError("No platform avg CSVs found. Run aggregate scripts first.")

n_platforms = len(platforms)
print(f"\nRunning with {n_platforms} platform(s): {list(platforms.keys())}")

# ── Global normalisation ──────────────────────────────────────────────────────
combined = pd.concat(list(platforms.values()), ignore_index=True)
combined["n_energy"] = minmax_global(combined["energy_j"])
combined["n_time"]   = minmax_global(combined["time_s"])
combined["n_edp"]    = minmax_global(combined["edp"])   # reference only
combined["ges"]      = W_ENERGY * combined["n_energy"] + W_TIME * combined["n_time"]
combined = add_rankings(combined)

combined.to_csv("results/processed/combined_metrics.csv", index=False)
print("Saved: results/processed/combined_metrics.csv")

# ── Per-platform metrics ───────────────────────────────────────────────────────
for platform, pf in platforms.items():
    pf = pf.copy()
    pf["n_energy_local"] = minmax_local(pf["energy_j"])
    pf["n_time_local"]   = minmax_local(pf["time_s"])
    pf["ges_local"]      = W_ENERGY * pf["n_energy_local"] + W_TIME * pf["n_time_local"]
    pf["ges_global"]     = combined.loc[combined["platform"] == platform, "ges"].values
    pf = add_rankings(pf, ges_col="ges_global")
    pf.to_csv(f"results/processed/{platform}_metrics.csv", index=False)
    print(f"Saved: results/processed/{platform}_metrics.csv")

# ── Statistical tests ─────────────────────────────────────────────────────────
kw_results = []

for platform in ("amd", "arm", "intel"):
    raw_path = f"results/processed/{platform}_results_ok.csv"
    if not os.path.exists(raw_path):
        print(f"ℹ  {raw_path} not found — skipping stats for {platform.upper()}.")
        continue

    raw = pd.read_csv(raw_path)
    pf_metrics = pd.read_csv(f"results/processed/{platform}_metrics.csv")
    raw = raw.merge(
        pf_metrics[["category","algorithm","language","ges_global"]],
        on=["category","algorithm","language"], how="left"
    ).dropna(subset=["ges_global"])

    groups = [g["ges_global"].values for _, g in raw.groupby("language")]
    if len(groups) < 2:
        continue

    stat, p = kruskal(*groups)
    kw_results.append({
        "platform": platform,
        "H_statistic": round(stat, 4),
        "p_value": round(p, 6),
        "n_observations": sum(len(g) for g in groups),
        "significant_p005": p < 0.05,
    })
    print(f"\nKruskal-Wallis [{platform.upper()}]: H={stat:.3f}, p={p:.4f}  →  "
          f"{'✅ SIGNIFICANT' if p < 0.05 else '❌ NOT significant'}")

    if POSTHOC_AVAILABLE:
        dunn = sp.posthoc_dunn(raw, val_col="ges_global", group_col="language",
                               p_adjust="bonferroni")
        dunn.to_csv(f"results/processed/dunn_posthoc_{platform}.csv")
        print(f"Saved: results/processed/dunn_posthoc_{platform}.csv")
        print(dunn.round(4).to_string())

if kw_results:
    pd.DataFrame(kw_results).to_csv("results/processed/kruskal_wallis.csv", index=False)
    print("\nSaved: results/processed/kruskal_wallis.csv")

# ── Cross-platform language summary ───────────────────────────────────────────
print("\n── Language Rankings (mean ges_global, lower = better) ──")
summary = combined.groupby(["platform","language"])["ges"].mean().unstack("language")
print(summary.round(4).to_string())

print("\n── Overall GES by language (all platforms pooled) ──")
overall = combined.groupby("language")["ges"].mean().sort_values()
print(overall.round(4).to_string())

print("\n✅ compute_metrics.py complete.")
print("\nOutputs:")
print("  combined_metrics.csv        — globally normalised, all platforms")
print("  {amd,arm,intel}_metrics.csv — per-platform GES + ranks")
print("  kruskal_wallis.csv          — KW test results per platform")
print("  dunn_posthoc_*.csv          — pairwise p-values (Bonferroni)")
