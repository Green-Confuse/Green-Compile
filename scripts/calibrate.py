#!/usr/bin/env python3
"""
calibrate.py — measure how long each benchmark actually runs, and report the
multiplier needed to reach a target duration.

Run this AFTER verify_parity.sh passes and BEFORE run_all_arm.sh.

The previous suite's scale_benchmarks.py patched 9 of 20 benchmarks and
skipped language files within those 9 (the C++ newton_raphson and
matrix_multiplication were never scaled). This script does not edit source --
it measures and tells you exactly what to change, so the edit is reviewed.
"""
import argparse, glob, os, subprocess, time, statistics as st, sys, json

def timeit(cmd, cwd=None, reps=3, timeout=900):
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        try:
            subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        ts.append(time.perf_counter() - t)
    return min(ts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=float, default=5.0)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--out", default="results/processed/calibration.json")
    a = ap.parse_args()

    rows = []
    for d in sorted(glob.glob("benchmarks/*/*")):
        if not os.path.isdir(d): continue
        algo, cat = os.path.basename(d), os.path.basename(os.path.dirname(d))
        rec = {"category": cat, "algorithm": algo, "times": {}}
        for lang in ["c","cpp","go","java","rust"]:
            if lang == "java":
                p = os.path.join(d,"java","Main.class")
                t = timeit(["java","-cp",".","Main"], cwd=os.path.join(d,"java"),
                           reps=a.reps) if os.path.exists(p) else None
            else:
                p = os.path.join(d,lang,"benchmark")
                t = timeit([os.path.abspath(p)], reps=a.reps) if os.access(p, os.X_OK) else None
            rec["times"][lang] = t
        rows.append(rec)

    print(f"{'benchmark':32s} " + " ".join(f"{l:>9s}" for l in
          ["c","cpp","go","java","rust"]) + f"  {'fastest':>9s} {'x needed':>9s}")
    print("-"*32 + " " + "-"*62)
    todo = []
    for r in rows:
        vals = [v for v in r["times"].values() if v]
        if not vals:
            print(f"{r['algorithm']:32s}  (no binaries built)"); continue
        fastest = min(vals)
        mult = a.target / fastest
        cells = " ".join(f"{(f'{v:.3f}' if v else '--'):>9s}" for v in
                         [r["times"][l] for l in ["c","cpp","go","java","rust"]])
        flag = "" if mult <= 1.0 else f"{mult:8.0f}x"
        print(f"{r['algorithm']:32s} {cells} {fastest:9.3f} {flag:>9s}")
        r["fastest_s"] = fastest; r["multiplier_needed"] = round(mult,1)
        if mult > 1.0: todo.append((r['algorithm'], round(mult,1), fastest))

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump({"target_s": a.target, "results": rows}, open(a.out,"w"), indent=2)

    print(f"\nTarget: {a.target}s on the FASTEST language of each benchmark.")
    if todo:
        print(f"\n{len(todo)} benchmarks still below target — scale these "
              f"workload constants (in ALL FIVE language files):")
        for algo, m, f_ in sorted(todo, key=lambda x:-x[1]):
            print(f"   {algo:32s} currently {f_:7.3f}s   multiply workload by ~{m:.0f}")
        print("\nAfter editing, re-run verify_parity.sh (workload params must "
              "still match across languages), then re-run this script.")
    else:
        print("\nAll benchmarks meet the target. Proceed to run_all_arm.sh.")
    print(f"\nSaved: {a.out}")

if __name__ == "__main__":
    main()
