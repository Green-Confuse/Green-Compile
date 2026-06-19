# Command Line Argument Parser Benchmark

**Category:** Mixed  
**Source:** https://rosettacode.org/wiki/Command-line_arguments  

## Description
Parses a fixed set of command-line arguments to extract flags and key-value
pairs. The benchmark exercises basic string scanning and conditional logic.

## Input Configuration
- Expects a fixed argument list supplied by the runner
- Recommended args:
  `--mode fast --size 1024 --verbose --name GreenCompile --repeat 5`

## Characteristics
- Single-threaded
- CPU-bound with light memory activity
- No external dependencies

## Benchmark Rationale
Command-line parsing is a common startup task that stresses string comparisons,
branching, and small-map updates.
