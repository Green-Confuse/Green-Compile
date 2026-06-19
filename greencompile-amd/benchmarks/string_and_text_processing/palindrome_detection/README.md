# Palindrome Detection Benchmark

**Category:** String and Text Processing  
**Source:** https://rosettacode.org/wiki/Palindrome_detection  

## Description
Checks whether strings are palindromes after normalizing case and removing
non-alphanumeric characters. The benchmark runs through a fixed dataset to
exercise string filtering and comparison.

## Input Configuration
- Uses a fixed ASCII string list embedded in the program
- Repeats the list to increase workload

## Characteristics
- Single-threaded
- CPU-bound with light memory activity
- No external dependencies

## Benchmark Rationale
Palindrome detection stresses character classification, normalization, and
string scanning, representative of common text preprocessing workloads.
