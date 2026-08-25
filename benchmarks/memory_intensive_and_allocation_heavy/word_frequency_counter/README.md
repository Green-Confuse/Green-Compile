# Word Frequency Counter Benchmark

**Category:** String and Text Processing  
**Source:** https://rosettacode.org/wiki/Word_frequency  

## Description
Counts the frequency of words in a fixed text sample. The benchmark tokenizes
input, normalizes case, and updates a frequency table, stressing string parsing
and dictionary operations.

## Input Configuration
- Uses a fixed ASCII text sample embedded in the program
- The sample is processed repeatedly to increase workload

## Characteristics
- Single-threaded
- CPU-bound with moderate memory activity
- No external dependencies

## Benchmark Rationale
Word frequency counting exercises text parsing, hashing, and dictionary updates,
which are common in real-world text workloads.
