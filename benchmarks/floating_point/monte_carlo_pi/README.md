# Monte Carlo Pi Benchmark

**Category:** Floating-Point / Numerical Computation  
**Source:** https://rosettacode.org/wiki/Monte_Carlo_methods  

## Description
The Monte Carlo Pi benchmark estimates pi using a fixed-seed PRNG and
random point sampling inside the unit square. It stresses floating-point
arithmetic and branch-heavy loops without external libraries or I/O.

## Input Configuration
- Samples = 10,000,000 (fixed)
- Deterministic PRNG (LCG), no I/O

## Characteristics
- Single-threaded
- CPU-bound
- Floating-point heavy
- No external dependencies
