# Onedigit Solver

<!-- TOC:START -->

- [Introduction](#introduction)
- [Terminology](#terminology)
- [Overview](#overview)
- [Process](#process)
- [Implementation](#implementation)
  - [Model Representation](#model-representation)
  - [Combo Representation](#combo-representation)

<!-- TOC:END -->

## Introduction

The objective of the Onedigit puzzle is to find arithmetic expressions (**combinations**) that evaluate to target values using only a single **digit** repeated multiple times and a set of allowed arithmetic operations.
The goal is to minimize the number of times the digit is used (the **cost**).
The solver finds combinations that satisfy the objective of the Onedigit puzzle.

## Terminology

Throughout this documentation, we use the terms:

- **base digit**: the single digit provided as input to the problem.
- **combination**: a valid arithmetic expression formed by applying operations to the base digit.
- **value**: the numeric result of evaluating a combination.
- **cost**: the number of base digits used in a combination.
  Example:
  - the cost of `3 + 3` is 2, since it uses two `3`s.
  - the cost of `33` is 2, since it uses two `3`s.
  - the cost of `3!` is 1, since it uses one `3`.
  - the cost of `(3!)!` is also 1, since it uses one `3`. Note that unary operators do not consume additional digits; they transform existing values.
- **generation**: an iteration of the search process where new combinations are formed from existing ones (referred to as "steps" in the CLI).

## Overview

We approach this as a search problem in the combination space.
This space can be visualized as a graph where:

- Each node represents a combination formed by applying an operation to 1 or 2 inputs.
- Each edge represents an input-output relationship between nodes through an operation.

The diagram below illustrates this structure.
Nodes visited during the same generation are highlighted in the same color, and nodes with thicker borders represent the lowest-cost combination for a given value.

![Solver combination space graph](images/combination-space.svg)

In the example above, there are two ways to reach `6`: either `3 + 3` (cost: 2) or `3!` (cost: 1).
Since we seek the lowest-cost combinations, we would select `3!` over `3 + 3`.

Key observations:

- Multiple combinations with varying costs can reach the same value.
- Depending on the operations available, some values may not be reachable.
- A node's cost equals the sum of its input nodes' costs.
- The combination space is infinite.
  For example, with addition, we can keep adding the base digit indefinitely to reach arbitrarily large values.

The solver uses a breadth-first search (BFS) strategy to systematically explore combinations.

## Process

1. Start with the base digit as the initial combination.
2. Apply all available operations to existing combinations to generate new ones.
3. Track only the lowest-cost combination for each value discovered.
   When multiple combinations produce the same value at the same cost, only the first is retained.
4. Repeat steps 2-3 for a specified number of generations.

Let's walk through an example using digit `3` with addition, subtraction, and factorial operations.
For simplicity, we'll restrict results to positive integers up to 100 and run for 3 generations.

- **Generation 1**:
  - Known solutions: `{3}`, Candidates from previous generation (the initial state): `{3}`
  - `3! = 6` (cost: 1)
  - `3 + 3 = 6` (cost: 2); discarded, `6` already found with lower cost
  - `3 - 3 = 0` (cost: 2); discarded, only positive values sought
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

To produce the combinations on each generation, we:

- apply each unary operator to each known solution, and
- apply each binary operator to each pair of known solutions.

This naive approach re-discovers combinations and leads to combinatorial explosion as generations progress.
To mitigate this, we apply two key optimizations:

- **Forward progress**: Each generation only considers combinations that include at least one combination from the immediately previous generation.
  It can be a unary operation on a previous generation combination or a binary operation combining a previous generation combination with any known combination.
- **Operand ordering**: Order operands in descending order by their value when applying some binary operations.
  There are a few advantages to this:
  - This helps prevent computing the same result multiple times in different ways (e.g., `a + b` and `b + a`).
  - Avoids producing negative intermediate results from subtraction.
    We exclude negative intermediate values, since final results needing them can be represented using subtraction from positive values.
    Example: instead of `33 + (-3) = 30`, we can represent `30` as `33 - 3`.

  This optimization does not affect addition and multiplication (commutative operations) or division (since we only consider positive integer intermediate results).
  However, it is not applicable to exponentiation since `2^3 ≠ 3^2`.

## Implementation

The solver is implemented as an iterative process that builds combinations generation by generation.
It maintains a collection of known solutions and expands it by applying operations to combinations from the previous generation.
It is structured around two main classes: `Model` and `Combo`.

### Model Representation

The solver represents each problem as a `Model` object containing:

- The base digit
- The set of available operations
- The maximum target number
- The maximum number of generations to run
- A collection of the lowest-cost `Combo` for each value found

### Combo Representation

The solver represents each combination as a `Combo` object encapsulating:

- The value produced by the combination
- The arithmetic expression (in terms of the base digit and operations)
- The cost to produce that value
- A structured representation storing the input values and operation used

The `Combo` class is defined in `model.py` as follows:

```python
@dataclasses.dataclass
class Combo:
  value: int
  cost: int = 0
  expr_full: str = ""
  expr_simple: str = ""
```

There are two expression formats:

- `expr_full`: the full representation, which uses only the base digit and the allowed operations.
- `expr_simple`: a compact representation that connects the precursor combinations and an allowed operation.

For example, for base digit `3`, a possible combination for the value `10` could be represented as:

```python
combo_10 = Combo(
    value=10,
    cost=4,                          # using four 3's
    expr_full="(3 * 3) + (3 / 3)",   # actual solution
    expr_simple="9 + 1"              # derived from precursors
)
```

Here, `9` and `1` in `expr_simple` are the values of precursor combinations (`3 * 3` and `3 / 3` respectively).
This shows how a combination can be constructed from simpler combinations.

The allowed operations are:

- binary operators: "+", "-", "\*", "/", "^"
- unary operators: "√", "!"

The expression string can also include:

- parentheses: "(", ")".
  parentheses may be nested, and must be balanced
- spaces

#### Constraints and Conventions

**Value constraints:**

- Only positive integers (excluding zero) are considered
- Fractions, negative values, and imaginary numbers are excluded

**Digit usage conventions:**

- `expr_full` can only use the base digit
- `expr_simple` represents combinations using the values of precursor combinations (which may display as any digit 0-9), but cannot have a leading zero

#### Examples

Valid strings for `expr_full` with base digit `3`:

```txt
expr_full = "(3 * (33 - 3)) + ((3 ^ 3) / 3)"  # 39
expr_full = "3 * √(33 + 3)"                   # 18
expr_full = "333 - (3!)"                      # 327
```

Valid strings for `expr_full` with base digit `2`:

```txt
expr_full = "(( √2 + √(2)) ^ 2)"              # 8
```

Valid strings for `expr_simple`:

```txt
expr_simple = "9 * 80"                        # 720
expr_simple = "8 + 1"                         # 9
expr_simple = "6!"                            # 720
```
