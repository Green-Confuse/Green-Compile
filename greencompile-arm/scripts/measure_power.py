#!/usr/bin/env python3
"""
measure_power.py
================
Reads instantaneous total power from Raspberry Pi 5 PMIC using vcgencmd.
Prints a single float: total watts across all power rails.

Usage (from shell):
    watts=$(python3 scripts/measure_power.py)

Power = Σ (Voltage × Current) for every rail reported by vcgencmd pmic_read_adc.
This covers: CPU core, DDR memory, system rails, WiFi, HDMI — i.e. total board power.
"""

import re
import subprocess
import sys


def read_pmic_power() -> float:
    try:
        result = subprocess.run(
            ["vcgencmd", "pmic_read_adc"],
            capture_output=True, text=True, timeout=2
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"0.0", file=sys.stdout)
        print(f"ERROR: vcgencmd failed: {e}", file=sys.stderr)
        return 0.0

    currents: dict[str, float] = {}
    voltages: dict[str, float] = {}

    for line in result.stdout.strip().split("\n"):
        # Current line: "  VDD_CORE_A current(7)=0.69653990A"
        m = re.match(r"\s*(\S+)_A\s+current\(\d+\)=([0-9.]+)A", line)
        if m:
            currents[m.group(1)] = float(m.group(2))
            continue
        # Voltage line: "  VDD_CORE_V volt(15)=0.72070740V"
        m = re.match(r"\s*(\S+)_V\s+volt\(\d+\)=([0-9.]+)V", line)
        if m:
            voltages[m.group(1)] = float(m.group(2))

    total_w = sum(
        currents[rail] * voltages[rail]
        for rail in currents
        if rail in voltages
    )
    return round(total_w, 6)


if __name__ == "__main__":
    print(read_pmic_power())
