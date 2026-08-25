# Anagram Checker Benchmark

**Category:** String and Text Processing  
**Source:** https://rosettacode.org/wiki/Anagrams  

## Description
Checks whether pairs of strings are anagrams after normalizing case and removing
non-alphanumeric characters. The benchmark stresses character filtering, hashing,
and comparison.

## Input Configuration
- Uses a fixed ASCII string pair list embedded in the program
- Repeats the checks to increase workload

## Characteristics
- Single-threaded
- CPU-bound with light memory activity
- No external dependencies

## Benchmark Rationale
Anagram checking is a common text task that exercises normalization and frequency
counting, representative of string-processing workloads.
