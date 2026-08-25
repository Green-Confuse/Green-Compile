#!/usr/bin/env python3
"""
analyze_all.py — combine the three platforms and run the corrected analysis.

Replaces compute_metrics.py. Four changes that a SUSCOM reviewer will look for:

  1. PER-BENCHMARK RATIO NORMALISATION + GEOMETRIC MEAN, alongside the old
     global min-max. Global min-max lets a single extreme configuration set
     the scale for all 300: in the published run the implied energy range was
     ~0.006 J to ~24 J, so almost every point sat in the bottom 2% of [0,1]
     (hence language means of 0.018-0.064 with SD bars of +/-0.15). Reporting
     BOTH schemes, and showing the ranking survives both, is the fix.

  2. BLOCKED STATISTICS. The old pipeline ran Kruskal-Wallis over n=1000
     per-run values per platform, treating 10 repetitions of each
     benchmark-language pair as independent. They are pseudo-replicates of 20
     units, which inflated H to 191-231 and made the p-values meaningless.
     Correct design: Friedman across 5 languages with benchmarks as blocks,
     Nemenyi post-hoc, Kendall's W as effect size.

  3. EFFECT SIZES. Cliff's delta for every language pair.

  4. NE/NT COLLINEARITY IS REPORTED, not assumed. If the two GES components
     are near-collinear the composite adds nothing and RQ3 must say so.

Usage:
    python3 scripts/analyze_all.py \
        --amd   amd_results.csv \
        --intel intel_results.csv \
        --arm   arm_results.csv \
        --outdir results/processed
"""

import argparse
import itertools
import os

import numpy as np
import pandas as pd
from scipy import stats

LANGS = ["c", "cpp", "go", "java", "rust"]


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((a[:, None] > b[None, :]).sum(axis=1))
    lt = sum((a[:, None] < b[None, :]).sum(axis=1))
    d = (gt - lt) / (len(a) * len(b))
    m = abs(d)
    mag = ("negligible" if m < 0.147 else "small" if m < 0.33
           else "medium" if m < 0.474 else "large")
    return d, mag


def nemenyi(ranks_matrix, k, n):
    """Nemenyi post-hoc from a blocks x treatments rank matrix."""
    avg = ranks_matrix.mean(axis=0)
    se = np.sqrt(k * (k + 1) / (6.0 * n))
    out = {}
    for i, j in itertools.combinations(range(k), 2):
        q = abs(avg[i] - avg[j]) / se
        # studentised range -> p, via the normal approximation used by Nemenyi
        p = min(1.0, 2 * (1 - stats.norm.cdf(q / np.sqrt(2))) * k * (k - 1) / 2)
        out[(i, j)] = p
    return avg, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--amd", required=True)
    ap.add_argument("--intel", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--primary", choices=["dynamic","total"], default="dynamic")
    ap.add_argument("--outdir", default="results/processed")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    frames = []
    for name, path in [("amd", a.amd), ("intel", a.intel), ("arm", a.arm)]:
        d = pd.read_csv(path)
        d = d[d.status == "OK"].copy()
        d["platform"] = name
        frames.append(d)
        print(f"{name:6s}: {len(d):5d} OK runs, "
              f"runtime median {d.time_s.median():.3f} s, "
              f"power {d.power_w.min():.2f}-{d.power_w.max():.2f} W")
    raw = pd.concat(frames, ignore_index=True)

    # ── idle-correction health ──────────────────────────────────────────────
    print("\n=== Idle-correction diagnostics ===")
    print(f"{'platform':9s} {'runs':>6s} {'idle W':>8s} {'E_dyn/E_tot':>12s} "
          f"{'clamped':>9s}  verdict")
    fragile = []
    for p_ in ["amd", "intel", "arm"]:
        d_ = raw[raw.platform == p_]
        if not len(d_): continue
        snr = (d_.dynamic_energy_j / d_.energy_j).median()
        clamped = int((d_.dynamic_energy_j <= 0).sum())
        if snr < 0.30: fragile.append(p_)
        print(f"{p_:9s} {len(d_):6d} {d_.idle_power_w.iloc[0]:8.3f} {snr:12.3f} "
              f"{clamped:9d}  {'OK' if snr>=0.30 else 'FRAGILE - idle dominates'}")
    if fragile:
        print(f"\n  !! {', '.join(fragile)}: workload raises power <30% over idle.")
        print("     Dynamic energy there is mostly baseline error. Enlarge the")
        print("     workload, or use total energy and restrict to within-platform.")

    ECOL = "dynamic_energy_j" if a.primary == "dynamic" else "energy_j"
    print(f"\nPrimary energy metric: {ECOL}")

    # ── aggregate to benchmark x language x platform cells ──────────────────
    agg = raw.groupby(["platform", "category", "algorithm", "language"]).agg(
        time_s=("time_s", "mean"), time_sd=("time_s", "std"),
        energy_j=(ECOL, "mean"), energy_sd=(ECOL, "std"),
        energy_total_j=("energy_j", "mean"),
        power_w=("power_w", "mean"), n=("time_s", "size")).reset_index()
    agg["cv_time_pct"] = 100 * agg.time_sd / agg.time_s
    agg["cv_energy_pct"] = 100 * agg.energy_sd / agg.energy_j
    agg["edp"] = agg.energy_j * agg.time_s

    print(f"\nCells: {len(agg)}   CV(time) median {agg.cv_time_pct.median():.2f}%, "
          f"p95 {agg.cv_time_pct.quantile(.95):.2f}%")
    noisy = (agg.cv_time_pct > 5).sum()
    if noisy:
        print(f"  !! {noisy} cells with CV > 5% -- inspect before reporting.")

    # ── Scheme A: global min-max (the published method, kept for comparison) ─
    for col, new in [("energy_j", "n_energy"), ("time_s", "n_time")]:
        lo, hi = agg[col].min(), agg[col].max()
        agg[new] = (agg[col] - lo) / (hi - lo)
    agg["ges_global"] = 0.5 * agg.n_energy + 0.5 * agg.n_time

    # ── Scheme B: per-benchmark ratio to the best implementation, geo-mean ──
    for metric in ["energy_j", "time_s"]:
        best = agg.groupby(["platform", "algorithm"])[metric].transform("min")
        agg[f"ratio_{metric}"] = agg[metric] / best
    agg["ges_ratio"] = np.sqrt(agg.ratio_energy_j * agg.ratio_time_s)

    agg.to_csv(f"{a.outdir}/combined_metrics.csv", index=False)

    # ── collinearity ────────────────────────────────────────────────────────
    pear = np.corrcoef(agg.n_energy, agg.n_time)[0, 1]
    spear = stats.spearmanr(agg.n_energy, agg.n_time).statistic
    print(f"\nNE vs NT:  Pearson {pear:.4f}   Spearman {spear:.4f}")
    print("  -> " + ("near-collinear; GES adds little over either component alone"
                     if pear > 0.95 else
                     "not collinear; the composite carries information"))

    # ── rankings under both schemes ─────────────────────────────────────────
    print("\n=== Language ranking ===")
    r1 = agg.groupby("language").ges_global.mean().sort_values()
    r2 = agg.groupby("language").ges_ratio.apply(
        lambda s: float(stats.gmean(s))).sort_values()
    cmp = pd.DataFrame({
        "global_minmax": r1, "rank_A": range(1, len(r1) + 1)}).join(
        pd.DataFrame({"ratio_geomean": r2, "rank_B": range(1, len(r2) + 1)}))
    print(cmp.to_string(float_format=lambda x: f"{x:.4f}"))
    if list(r1.index) != list(r2.index):
        print("\n  !! The two normalisation schemes DISAGREE on the ordering.")
        print("     Report both and do not present either as definitive.")
    else:
        print("\n  Ordering is stable across both normalisation schemes.")

    # ── per-platform ranking + cross-platform agreement ─────────────────────
    from scipy.stats import gmean as _gm
    print("\n=== Per-platform language ranking (ratio + geometric mean) ===")
    per = {}
    for p_ in ["amd", "intel", "arm"]:
        sub = agg[agg.platform == p_]
        if not len(sub): continue
        srs = sub.groupby("language").ges_ratio.apply(lambda x: float(_gm(x)))
        per[p_] = srs
        print(f"  {p_:6s}  " + "  ".join(f"{k}={srs[k]:.3f}" for k in LANGS))
        print(f"          {' < '.join(srs.sort_values().index)}")
    per_df = pd.DataFrame(per)
    per_df.to_csv(f"{a.outdir}/per_platform_ranking.csv")

    print("\n=== Cross-platform agreement of the LANGUAGE ranking ===")
    print("  (domain-free: each platform is ranked against itself, so")
    print("   RAPL-vs-PMIC never enters the comparison)")
    rows_ = []
    for p_, q_ in itertools.combinations(list(per_df.columns), 2):
        rho = stats.spearmanr(per_df[p_].rank(), per_df[q_].rank()).statistic
        tau = stats.kendalltau(per_df[p_].rank(), per_df[q_].rank()).statistic
        rows_.append(dict(a=p_, b=q_, spearman=rho, kendall=tau))
        print(f"  {p_:6s} vs {q_:6s}   Spearman {rho:+.3f}   Kendall {tau:+.3f}")
    pd.DataFrame(rows_).to_csv(f"{a.outdir}/cross_platform_agreement.csv", index=False)

    print("\n  Benchmark-level rank reversals (winner differs by platform):")
    piv = agg.pivot_table(index=["algorithm","platform"], columns="language",
                          values="ges_ratio")
    rev = []
    for alg in agg.algorithm.unique():
        w = {}
        for p_ in per_df.columns:
            try: w[p_] = piv.loc[(alg, p_)].idxmin()
            except KeyError: pass
        if len(w) > 1 and len(set(w.values())) > 1:
            rev.append(dict(algorithm=alg, **w))
    if rev:
        print(pd.DataFrame(rev).to_string(index=False))
        print(f"\n  {len(rev)}/{agg.algorithm.nunique()} benchmarks change winner")
        print("  across platforms -- this is the real, defensible answer to RQ2.")
    else:
        print("  None -- the winner is identical on all three platforms.")
    pd.DataFrame(rev).to_csv(f"{a.outdir}/rank_reversals.csv", index=False)

    # ── blocked statistics, per platform ────────────────────────────────────
    print("\n=== Friedman (blocked by benchmark) + Nemenyi ===")
    stat_rows, pair_rows = [], []
    for plat in ["amd", "intel", "arm"]:
        p = agg[agg.platform == plat]
        wide = p.pivot_table(index="algorithm", columns="language",
                             values="ges_ratio")
        wide = wide.dropna()[LANGS]
        if len(wide) < 3:
            continue
        chi, pv = stats.friedmanchisquare(*[wide[l].values for l in LANGS])
        n, k = wide.shape
        W = chi / (n * (k - 1))            # Kendall's W
        print(f"\n{plat.upper()}  chi2={chi:.3f}  df={k-1}  p={pv:.3e}  "
              f"n_blocks={n}  Kendall W={W:.3f} "
              f"({'small' if W<0.3 else 'moderate' if W<0.5 else 'strong'} agreement)")
        stat_rows.append(dict(platform=plat, chi2=chi, df=k - 1, p=pv,
                              n_blocks=n, kendall_w=W))

        ranks = wide.rank(axis=1).values
        avg, pvals = nemenyi(ranks, k, n)
        print("   mean rank: " + "  ".join(f"{l}={avg[i]:.2f}" for i, l in enumerate(LANGS)))
        for (i, j), pp in sorted(pvals.items(), key=lambda x: x[1]):
            d, mag = cliffs_delta(wide[LANGS[i]].values, wide[LANGS[j]].values)
            sig = "*" if pp < 0.05 else " "
            print(f"   {LANGS[i]:5s} vs {LANGS[j]:5s}  p={pp:7.4f}{sig}  "
                  f"delta={d:+.3f} ({mag})")
            pair_rows.append(dict(platform=plat, a=LANGS[i], b=LANGS[j],
                                  p_nemenyi=pp, cliffs_delta=d, magnitude=mag))

    pd.DataFrame(stat_rows).to_csv(f"{a.outdir}/friedman.csv", index=False)
    pd.DataFrame(pair_rows).to_csv(f"{a.outdir}/nemenyi_posthoc.csv", index=False)

    print(f"\nWrote combined_metrics.csv, friedman.csv, nemenyi_posthoc.csv "
          f"to {a.outdir}")
    print("\n" + "="*70)
    print("NOT PRODUCED, DELIBERATELY: architecture-level energy ranking.")
    print("Deciding whether ARM, AMD or Intel is 'greener' needs ONE instrument")
    print("measuring ONE domain across all three machines. RAPL reads the CPU")
    print("package; the Pi 5 PMIC reads the whole board. The published claim")
    print("that ARM wins 17 of 20 benchmarks is an artifact of min-max mapping")
    print("the smaller-magnitude domain to ~0.")
    print("SUPPORTED: language ranking within each platform, and how well those")
    print("rankings agree across platforms (see above).")
    print("="*70)


if __name__ == "__main__":
    main()
