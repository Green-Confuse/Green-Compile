# Producer–Consumer (Single-Thread) Benchmark

**Category:** Mixed  
**Source:** https://rosettacode.org/wiki/Producer-consumer_problem  

## Description
Implements a single-threaded producer–consumer pipeline using a ring buffer.
The producer generates integers and the consumer drains them, exercising queue
management, modular arithmetic, and loop control without threading overhead.

## Input Configuration
- Fixed number of items per iteration
- Repeats the producer–consumer cycle to increase workload

## Characteristics
- Single-threaded
- CPU-bound with light memory activity
- No external dependencies

## Benchmark Rationale
Producer–consumer patterns model pipeline coordination and buffering. A single-
threaded variant isolates queue mechanics and control flow costs.
