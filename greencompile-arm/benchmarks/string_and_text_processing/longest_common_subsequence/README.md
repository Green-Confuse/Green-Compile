# Longest Common Subsequence Benchmark

**Category:** String and Text Processing  
**Source:** https://rosettacode.org/wiki/Longest_common_subsequence  

## Description
Computes the length of the longest common subsequence (LCS) between two fixed
strings using dynamic programming. This stresses character comparison, DP table
updates, and memory access patterns.

## Input Configuration
- Uses two fixed ASCII strings embedded in the program
- Repeats the computation to increase workload

## Characteristics
- Single-threaded
- CPU-bound with moderate memory activity
- No external dependencies

## Benchmark Rationale
LCS is a classic text-processing DP problem that exercises nested loops and
array updates common in string analysis workloads.
