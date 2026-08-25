# Towers of Hanoi Benchmark

**Category:** Computational / Algorithmic  
**Source:** https://rosettacode.org/wiki/Towers_of_Hanoi  

## Description
The Towers of Hanoi benchmark evaluates recursive control-flow performance.
It stresses function calls, stack usage, and branch execution without relying
on external libraries or parallel execution.

## Input Configuration
- Number of disks (N): 20
- Fixed input to ensure determinism and reproducibility

## Characteristics
- Single-threaded
- CPU-bound
- No I/O during execution
- No external dependencies

## Usage
Each implementation is compiled with default optimization flags and executed
multiple times to obtain stable energy and time measurements.
