#!/usr/bin/env python3
"""
pmic_sampler.py — persistent Raspberry Pi 5 PMIC power sampler.

Replaces the original two-sample (before/after) approach in run_all_arm.sh,
which produced energy = P_idle * T and therefore contained no workload signal.

Runs as ONE long-lived process for the whole measurement session and appends
timestamped samples to a CSV. run_all_arm.sh records t_start/t_end per
benchmark run; integrate_energy.py then slices this CSV by timestamp and
performs real trapezoidal integration over the execution window.

Why one persistent process instead of start/stop per run:
  - `vcgencmd` costs ~5-30 ms per call; a per-run sampler would pay Python
    interpreter startup (~30 ms) on top of that, which is the same class of
    bug we are fixing.
  - A continuously running sampler has constant overhead that is present
    during BOTH the idle-baseline window and the measured windows, so it
    largely cancels in the idle-corrected dynamic energy.

Usage:
    python3 scripts/pmic_sampler.py --out results/raw/pmic_samples.csv \
        --interval 0.005 &
    echo $! > /tmp/sampler.pid
    ...
    kill "$(cat /tmp/sampler.pid)"

Output columns: t_ns,watts   (t_ns is CLOCK_REALTIME nanoseconds, matching
`date +%s%N` used by the bash harness)
"""

import argparse
import os
import re
import signal
import subprocess
import sys
import time

CUR_RE = re.compile(r"\s*(\S+)_A\s+current\(\d+\)=([0-9.]+)A")
VOLT_RE = re.compile(r"\s*(\S+)_V\s+volt\(\d+\)=([0-9.]+)V")

_running = True


def _stop(signum, frame):
    global _running
    _running = False


def read_power():
    """Return (total_watts, n_rails) or (None, 0) on failure."""
    try:
        r = subprocess.run(["vcgencmd", "pmic_read_adc"],
                           capture_output=True, text=True, timeout=2)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, 0

    currents, voltages = {}, {}
    for line in r.stdout.splitlines():
        m = CUR_RE.match(line)
        if m:
            currents[m.group(1)] = float(m.group(2))
            continue
        m = VOLT_RE.match(line)
        if m:
            voltages[m.group(1)] = float(m.group(2))

    rails = [k for k in currents if k in voltages]
    if not rails:
        return None, 0
    return sum(currents[k] * voltages[k] for k in rails), len(rails)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--interval", type=float, default=0.005,
                    help="target seconds between samples; the true rate is "
                         "bounded below by vcgencmd latency")
    ap.add_argument("--flush-every", type=int, default=20)
    args = ap.parse_args()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    p, n_rails = read_power()
    if p is None:
        sys.stderr.write("FATAL: vcgencmd pmic_read_adc produced no usable "
                         "rails. Are you on a Raspberry Pi 5?\n")
        sys.exit(1)
    sys.stderr.write(f"pmic_sampler: {n_rails} rails, first reading {p:.4f} W\n")

    n = 0
    with open(args.out, "w", buffering=1024 * 64) as f:
        f.write("t_ns,watts\n")
        while _running:
            t = time.time_ns()
            w, _ = read_power()
            if w is not None:
                f.write(f"{t},{w:.6f}\n")
                n += 1
                if n % args.flush_every == 0:
                    f.flush()
            if args.interval > 0:
                time.sleep(args.interval)
        f.flush()
    sys.stderr.write(f"pmic_sampler: wrote {n} samples to {args.out}\n")


if __name__ == "__main__":
    main()
