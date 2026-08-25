#!/usr/bin/env python3
"""
integrate_energy.py — turn the raw PMIC sample stream + per-run timestamps
into real integrated energy.

This is the code that Equation 16 of the manuscript describes and that the
original run_all_arm.sh did not contain.

Inputs
  --samples  results/raw/pmic_samples.csv   (t_ns,watts from pmic_sampler.py)
  --runs     results/raw/arm_runs.csv       (per-run metadata incl. t_start_ns,
                                             t_end_ns, written by run_all_arm.sh)
  --idle     results/processed/idle_power_w.txt
Output
  --out      results/raw/arm_results.csv    (same schema as before, plus
                                             n_samples so reviewers can audit)

For each run we take every sample inside [t_start, t_end], add linearly
interpolated endpoints at exactly t_start and t_end, and apply the composite
trapezoidal rule. Runs with fewer than MIN_SAMPLES interior samples are marked
FAIL_UNDERSAMPLED rather than silently reported -- an undersampled run is not
a measurement, and the previous pipeline's habit of emitting a number anyway
is what produced 1,000 rows of idle power.
"""

import argparse
import csv
import sys

import numpy as np
import pandas as pd

MIN_SAMPLES = 20


def integrate(ts, ws, t0, t1):
    """Composite trapezoidal integral of power over [t0, t1] -> joules.

    ts in ns, ws in W. Endpoints are linearly interpolated so the window is
    exactly [t0, t1] and not merely the samples that happen to fall inside.
    """
    lo = np.searchsorted(ts, t0, side="left")
    hi = np.searchsorted(ts, t1, side="right")
    inner_t, inner_w = ts[lo:hi], ws[lo:hi]
    n_inner = len(inner_t)
    if n_inner == 0:
        return None, 0

    def interp(t):
        return float(np.interp(t, ts, ws))

    t_arr = np.concatenate(([t0], inner_t, [t1])).astype(np.float64)
    w_arr = np.concatenate(([interp(t0)], inner_w, [interp(t1)]))
    # np.trapezoid on seconds
    joules = float(np.trapezoid(w_arr, t_arr / 1e9))
    return joules, n_inner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--idle", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-samples", type=int, default=MIN_SAMPLES)
    args = ap.parse_args()

    s = pd.read_csv(args.samples).sort_values("t_ns")
    ts = s.t_ns.values.astype(np.int64)
    ws = s.watts.values.astype(np.float64)
    idle = float(open(args.idle).read().strip())

    runs = pd.read_csv(args.runs)
    out_rows, n_bad = [], 0

    for _, r in runs.iterrows():
        t_s = (r.t_end_ns - r.t_start_ns) / 1e9
        ej, n = integrate(ts, ws, r.t_start_ns, r.t_end_ns)

        if ej is None or n < args.min_samples:
            n_bad += 1
            status = "FAIL_UNDERSAMPLED"
            ej = dyn = pw = ""
        elif int(r.exit_code) != 0:
            status = "FAIL"
            dyn = max(0.0, ej - idle * t_s)
            pw = ej / t_s if t_s > 0 else 0.0
        else:
            status = "OK"
            dyn = max(0.0, ej - idle * t_s)
            pw = ej / t_s if t_s > 0 else 0.0

        out_rows.append({
            "category": r.category, "algorithm": r.algorithm,
            "language": r.language, "run": r.run, "status": status,
            "time_s": round(t_s, 9),
            "energy_j": round(ej, 9) if ej != "" else "",
            "dynamic_energy_j": round(dyn, 9) if dyn != "" else "",
            "power_w": round(pw, 6) if pw != "" else "",
            "idle_power_w": idle,
            "n_samples": n,
            "domain": "vcgencmd_pmic_board",
            "energy_path": "vcgencmd pmic_read_adc (async sampled)",
            "exit_code": int(r.exit_code),
        })

    df = pd.DataFrame(out_rows)
    df.to_csv(args.out, index=False)

    ok = df[df.status == "OK"]
    print(f"Wrote {len(df)} rows -> {args.out}")
    print(f"  OK                : {len(ok)}")
    print(f"  FAIL_UNDERSAMPLED : {n_bad}   (< {args.min_samples} samples in window)")
    print(f"  FAIL (exit code)  : {(df.status == 'FAIL').sum()}")
    if len(ok):
        print(f"\n  samples/run       : median {ok.n_samples.median():.0f}, "
              f"min {ok.n_samples.min()}, max {ok.n_samples.max()}")
        print(f"  runtime           : median {ok.time_s.median():.3f} s, "
              f"min {ok.time_s.min():.3f} s")
        print(f"  active power      : {ok.power_w.min():.3f} - "
              f"{ok.power_w.max():.3f} W   (idle baseline {idle:.3f} W)")
        below = (ok.power_w < idle).sum()
        if below:
            print(f"\n  !! {below} runs report active power BELOW idle. "
                  f"That was the original bug -- investigate before proceeding.")
        else:
            print("\n  OK: every run reports active power above the idle "
                  "baseline, i.e. the sampler is seeing the workload.")
    if n_bad:
        print(f"\n  !! {n_bad} runs undersampled. Increase workload size or "
              f"sampler rate; do NOT report these.")


if __name__ == "__main__":
    main()
