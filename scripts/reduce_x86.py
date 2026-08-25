#!/usr/bin/env python3
"""
reduce_x86.py — turn raw RAPL counter pairs into energy, with the checks the
original pipeline lacked.

All arithmetic lives here rather than in the measurement loop, so that no
Python interpreter is ever launched between the two counter reads.

Three things this does that the old pipeline did not:

  1. HANDLES COUNTER WRAPAROUND. The old script tested `(( e2 >= e1 ))` and
     marked the run FAIL otherwise, silently discarding every run that
     straddled a wrap of max_energy_range_uj.

  2. ASSERTS PHYSICAL PLAUSIBILITY. Any run whose average package power
     exceeds the part's PL2 is failed, not reported. The published tables
     contain 99.5 W on a 28 W Intel part and 83.4 W on a 15 W AMD part; an
     assertion here would have caught that before submission.

  3. FLAGS A CONSTANT ENERGY OFFSET. Fits E = E0 + P*T across all
     configurations. A large intercept means untimed work is inside the energy
     window -- exactly the 429 mJ sudo bug. This runs automatically and warns.
"""

import argparse
import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--idle", required=True)
    ap.add_argument("--pl-max", type=float, required=True)
    ap.add_argument("--domain", default="package-0")
    ap.add_argument("--energy-path", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-offset-mj", type=float, default=20.0)
    a = ap.parse_args()

    r = pd.read_csv(a.runs)
    idle = float(open(a.idle).read().strip())

    d_uj = (r.e_end_uj - r.e_start_uj).astype(np.float64)
    wrapped = d_uj < 0
    d_uj = d_uj + wrapped * r.e_max_uj.astype(np.float64)

    out = pd.DataFrame({
        "platform": r.platform, "category": r.category, "algorithm": r.algorithm,
        "language": r.language, "run": r.run,
        "time_s": (r.t_end_us - r.t_start_us) / 1e6,
        "energy_j": d_uj / 1e6,
        "idle_power_w": idle,
        "counter_wrapped": wrapped.astype(int),
        "domain": a.domain, "energy_path": a.energy_path,
        "exit_code": r.exit_code,
    })
    out["power_w"] = out.energy_j / out.time_s
    out["dynamic_energy_j"] = (out.energy_j - idle * out.time_s).clip(lower=0)

    out["status"] = "OK"
    out.loc[out.exit_code != 0, "status"] = "FAIL"
    implausible = out.power_w > a.pl_max
    out.loc[implausible, "status"] = "FAIL_IMPLAUSIBLE_POWER"
    zero_t = out.time_s <= 0
    out.loc[zero_t, "status"] = "FAIL_ZERO_TIME"

    out.to_csv(a.out, index=False)
    ok = out[out.status == "OK"]

    print(f"Wrote {len(out)} rows -> {a.out}")
    print(f"  OK                     : {len(ok)}")
    print(f"  FAIL (exit code)       : {(out.status == 'FAIL').sum()}")
    print(f"  FAIL_IMPLAUSIBLE_POWER : {implausible.sum()}  (> {a.pl_max} W)")
    print(f"  counter wraps handled  : {wrapped.sum()}")

    if not len(ok):
        print("\n  !! No usable runs.")
        return

    print(f"\n  runtime      : median {ok.time_s.median():.3f} s, "
          f"min {ok.time_s.min():.3f} s, max {ok.time_s.max():.3f} s")
    print(f"  package power: {ok.power_w.min():.2f} - {ok.power_w.max():.2f} W "
          f"(idle {idle:.2f} W, PL2 {a.pl_max:.0f} W)")

    # Offset diagnostic -- the 429 mJ test
    g = ok.groupby(["algorithm", "language"]).agg(
        time_s=("time_s", "mean"), energy_j=("energy_j", "mean")).reset_index()
    # The fit is only meaningful when runtimes span a range; if every
    # configuration lasts the same time, the intercept and slope are not
    # separately identifiable and the diagnostic must be skipped.
    t_spread = g.time_s.max() / max(g.time_s.min(), 1e-9)
    if len(g) < 10 or t_spread < 2.0:
        print(f"\n  Offset diagnostic skipped: runtimes span only "
              f"{t_spread:.2f}x, too narrow to separate intercept from slope.")
    else:
        A = np.vstack([np.ones(len(g)), g.time_s.values]).T
        (E0, P), *_ = np.linalg.lstsq(A, g.energy_j.values, rcond=None)
        pred = A @ np.array([E0, P])
        denom = ((g.energy_j - g.energy_j.mean()) ** 2).sum()
        ss = 1 - ((g.energy_j - pred) ** 2).sum() / denom if denom > 0 else float("nan")
        print(f"\n  Offset diagnostic:  E = {E0*1000:.1f} mJ + {P:.3f} W * T   "
              f"(R^2 = {ss:.3f})")
        if abs(E0) * 1000 > a.max_offset_mj:
            print(f"  !! Intercept {E0*1000:.0f} mJ exceeds {a.max_offset_mj:.0f} mJ.")
            print(f"     Untimed work is inside the energy window. This is the")
            print(f"     bug that produced the published 76-99 W figures.")
            print(f"     Equivalent to {E0/P*1000:.0f} ms of untimed activity.")
        else:
            print(f"  OK: intercept is small; the energy and timing windows agree.")
        if P > a.pl_max:
            print(f"  !! Fitted load power {P:.1f} W exceeds PL2 {a.pl_max:.0f} W.")

    short = (ok.time_s < 1.0).sum()
    if short:
        print(f"\n  !! {short}/{len(ok)} runs under 1 s. Startup overhead will")
        print(f"     dominate. Re-run calibrate.py with a larger target.")


if __name__ == "__main__":
    main()
