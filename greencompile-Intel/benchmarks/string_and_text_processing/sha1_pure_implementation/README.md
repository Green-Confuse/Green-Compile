# SHA-1 (Pure Implementation) Benchmark

**Category:** Mixed  
**Source:** https://rosettacode.org/wiki/SHA-1  

## Description
Computes SHA-1 on a fixed input buffer using a pure language implementation
without external crypto libraries. This stresses bit operations, rotations,
and block processing.

## Input Configuration
- Uses a fixed ASCII message embedded in the program
- Repeats hashing to increase workload

## Characteristics
- Single-threaded
- CPU-bound with moderate integer/bit operations
- No external dependencies

## Benchmark Rationale
SHA-1 is a classic hash workload that exercises tight loops and bitwise math,
useful for comparing compiler optimizations.
