# Onedigit Solver

The solver is designed to find combinations of a single digit and a set of arithmetic operations that can produce target values with the lowest cost (number of digits used).

NOTE: In this documentation, we use the terms:

- **base digit**: the single digit provided as input to the problem.
- **combination**: an arithmetic expression formed by applying operations to the base digit.
- **value**: the numeric result of evaluating a combination.
- **cost**: the number of base digits used in a combination.
- **generation**: an iteration of the search process where new combinations are formed from existing ones.
  Referred to as "steps" in the CLI.

## Overview

We approach this as a search problem in the combination space.
This space can be visualized as a graph where:

- Each node represents a combination formed by applying an operation to 1 or 2 inputs.
- Each edge represents an input-output relationship between nodes through an operation.

![Solver combination space graph](images/combination-space.svg)

Nodes visited during the same generation are highlighted in the same color.
Nodes with thicker borders represent the lowest-cost combination for a given value.

The cost of a node is defined as the number of digits used in the combination.
In the example above, there are two ways to reach `6`: either `3 + 3` (cost: 2) or `3!` (cost: 1).
Since we're interested in finding combinations that produce target values with the lowest cost, we would select `3!` over `3 + 3`.

Key observations:

- Many numbers can be reached by multiple combinations with varying costs.
- Depending on the operations available, some numbers may not be reachable.
- A node's cost equals the sum of its input nodes' costs.
- The combination space is infinite.
  For example, with addition, we can keep adding the base digit indefinitely to reach arbitrarily large numbers.

Given this infinite space, we use a breadth-first search (BFS) strategy to systematically explore combinations.

## Process

1. Start with the base digit as the initial combination.
2. Apply all available operations to existing combinations to generate new ones.
3. Track the lowest-cost combination for each value discovered.
4. Repeat steps 2-3 for a specified number of generations.

Let's walk through an example using digit `3` with addition, subtraction, and factorial operations.
For simplicity, we'll restrict results to positive integers up to 100 and run for 3 generations.

- **Generation 1**:
  - Known solutions: `{3}`, Candidates from previous generation: `{3}`
  - `3! = 6` (cost: 1)
  - `3 + 3 = 6` (cost: 2); discarded, `6` already found with lower cost
  - `3 - 3 = 0` (cost: 2); discarded, only positive numbers sought
- **Generation 2**:
  - Known solutions: `{3, 6}`, Candidates from previous generation: `{6}`
  - `6! = 720` (cost: 1); discarded, exceeds limit of 100
  - `6 + 3 = 9` (cost: 2)
  - `6 + 6 = 12` (cost: 2)
  - (some discarded combinations omitted for clarity)
- **Generation 3**:
  - Known solutions: `{3, 6, 9, 12}`, Candidates from previous generation: `{9, 12}`
  - `6 + 9 = 15` (cost: 3)
  - `9 + 9 = 18` (cost: 4)
  - `12 + 3 = 15` (cost: 3); discarded, `15` already found at same cost
  - `12 + 12 = 24` (cost: 4)
  - (some discarded combinations omitted for clarity)
- **Final results**:
  - `3` (cost: 1)
  - `6 = 3!` (cost: 1)
  - `9 = 3 + 6` (cost: 2)
  - `12 = 6 + 6` (cost: 2)
  - `15 = 6 + 9` (cost: 3)
  - `18 = 9 + 9` (cost: 4)
  - `24 = 12 + 12` (cost: 4)

To prevent combinatorial explosion, we apply several optimizations:

- **Forward progress**: Each generation only considers combinations that include at least one result from the immediately previous generation.
  For example, if `NEW` denotes a combination from the previous generation and `OLD` denotes any earlier combination, we consider `NEW + OLD` and `NEW + NEW`, but not `OLD + OLD`.
- **Commutative operations**: For addition and multiplication, we only consider one ordering of operands (e.g., `a + b` but not `b + a`).
- **Cost-based pruning**: We discard any combination that produces a value already discovered at equal or lower cost.

## Implementation

The solver represents each problem as a `Model` object containing:

- The base digit
- The set of available operations
- The maximum target number
- The maximum number of generations to run
- A collection of the lowest-cost `Combo` for each value found

The solver represents each combination as a `Combo` object encapsulating:

- The value produced by the combination
- The arithmetic expression (in terms of the base digit and operations)
- The cost to produce that value
- A structured representation storing the input values and operation used
