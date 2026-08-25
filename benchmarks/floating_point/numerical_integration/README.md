# Numerical Integration (Simpson/Trapezoidal) Benchmark

**Category:** Floating-Point / Numerical Computation  
**Source:** https://rosettacode.org/wiki/Numerical_integration  

## Description
This benchmark computes a fixed integral using both Simpson's rule and the
trapezoidal rule. It stresses floating-point arithmetic and loop-heavy
accumulation without external libraries or I/O.

## Input Configuration
- Integral: _0^1 4/(1+x^2) dx (pi approximation)
- Steps: 1,000,000 (fixed)
- Deterministic, no I/O

## Characteristics
- Single-threaded
- CPU-bound
- Floating-point heavy
- No external dependencies
