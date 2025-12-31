# Single Digit Combinations

As a kid, I saw a number puzzle in a newspaper that intrigued me.
The objective was to find the smallest expression that produced a given value using only a single digit and basic mathematical operations.

This package provides a solver for that puzzle.

## The Puzzle

It is easier to understand with an example.

> _Using only the digit `3`, and the basic operations of addition, subtraction, multiplication, and division, write an expression that evaluates to the number `75`._

Some possible combinations might be:

- $3 + 3 + 3 + ... + 3$ (25 times)
- $3 \times (3 \times 3 \times 3 - 3) + 3$
- $3 \times 3 \times 3 \times 3 - 3 - 3$

The goal is to find the expression with the lowest cost, where the cost of an expression is determined by the number of times the digit is used.
This first expression has a cost of `25`, while the second and third expressions have a cost of `6`.

More complex operations can be used to reduce the cost further, such as:

- Concatenation of the base digit (e.g., forming `3333` uses the digit `3` four times, giving a cost of `4`)
- Exponentiation
- Square root
- Factorial

| Expression                                | Operations         | Cost |
| :---------------------------------------- | ------------------ | ---: |
| $3 + 3 + 3 + ... + 3$ (25 times)          | `+`                |   25 |
| $33 + 33 + 3 + 3 + 3$                     | `+`, concatenation |    7 |
| $(3 \times (3 \times 3 \times 3- 3)) + 3$ | `+`, `-`, `*`      |    6 |
| $(3 \times 3^3 - 3) + 3$                  | `+`, `-`, `*`, `^` |    5 |
| $(3 \times 3^3) - (3!)$                   | `-`, `*`, `^`, `!` |    4 |

## Solver

The solver uses a generative approach to find combinations.
Starting from the base digit, it applies all possible operations to generate new numbers.
These new numbers are then used in subsequent steps to generate even more numbers.
The solver keeps the combinations with the lowest cost for each number generated.
This process continues for a specified number of steps or until no new numbers can be generated.

Example:

- Generation 1:
  - `3 = 3` (cost: 1)
- Generation 2:
  - `3! = 6` (cost: 1),
  - `3 * 3 = 9` (cost: 2),
  - `3 ^ 3 = 27` (cost: 2),
  - `3 / 3 = 1` (cost: 2),
  - ...
- Generation 3:
  - `3 * 6 = 18` (cost: 2),
  - `27 + 3 = 30` (cost: 3),
  - ...

## Prerequisites

- Python 3.9 or higher

## Installation

- Preferred method

  Install the package with `pip` (or your preferred package manager).
  This will make the `onedigit` CLI available in your environment.

  ```sh
  pip install onedigit
  ```

- Alternative method

  Clone the repository and install it locally:

  ```sh
  git clone https://github.com/jzer7/onedigit-py.git
  cd onedigit-py
  pip install .
  ```

- Direct execution

  This package has no external dependencies beyond the Python standard library, so it can also be used by running the `onedigit` script located in the `scripts` directory.

## Usage

The `onedigit` CLI provides access to the solver.
Use the `help` option to see all available parameters.

```sh
onedigit --help
```

```text
usage: onedigit [-h] [--max-value MAX_VALUE] [--max-cost MAX_COST]
                [--max-steps MAX_STEPS] [--full] [--input-filename INPUT_FILENAME]
                [--output-filename OUTPUT_FILENAME] digit

Calculate number combinations using a single digit.

positional arguments:
  digit                 The digit to use to generate combinations (1-9)

options:
  -h, --help            show this help message and exit
  --max-value MAX_VALUE
                        Largest value for a combination to be shown in the output (default: 9999)
  --max-cost MAX_COST   Maximum cost a combination can have for it to be remembered (default: 2)
  --max-steps MAX_STEPS
                        Maximum number of generative steps (default: 5)
  --full                Display combinations using full expressions instead of simple values
  --input-filename INPUT_FILENAME
                        JSON file used to preload the model
  --output-filename OUTPUT_FILENAME
                        JSON file used to store the model upon completion
```

Note: The default `max-cost` value (2) is intentionally low to prevent accidental long-running computations.
For meaningful results, explicitly set `--max-cost` to at least match `--max-steps`,
since expressions in the final generation typically have a cost equal to or greater than the number of steps.

### Examples

The simplest use is to get combinations using the digit `3`:

```sh
onedigit 3
```

Show the full expression for combinations using the digit `7` that result in values up to 100:

```sh
onedigit 7 --max-value 100 --full
```

Save combinations as a JSON file:

```sh
onedigit 7 --max-value 100 --output-filename example.json
```

### Incremental Computation

Computing combinations for large numbers can be time-consuming due to the exponential growth of possible expressions.
The solver can be run incrementally by seeding it with results from a previous run.
This two-stage approach is significantly faster than computing high-cost expressions for large numbers in a single pass.

For example, we can first focus on obtaining high-quality combinations (low cost) for numbers up to `200`, which is relatively quick since we limit the range of values we retain.
Then we use those results as a starting point to search for combinations of larger numbers.

```sh
onedigit 3 --max-value 200 --max-steps 9 --max-cost 9 --output-filename snapshot_001.json
onedigit 3 --max-value 1000 --max-cost 9 --input-filename snapshot_001.json --output-filename snapshot_002.json
```

The above example running in a Raspberry Pi 3, takes about `0.25s` to generate combinations up to `200` with a maximum cost of `9`, and about `0.2s` to extend that to `1000`.
In contrast, producing expressions up to `1000` directly takes about `5s`.

### Querying the Output

The output JSON file contains all the combinations found.
It follows the format:

```json
{
  "digit": 3,
  "max_value": 100,
  "max_cost": 3,
  "combinations": [
    {
      "value": 1,
      "cost": 2,
      "expr_simple": "3/3",
      "expr_full": "(3)/(3)"
    },
    {
      "value": 2,
      "cost": 2,
      "expr_simple": "6/3",
      "expr_full": "(3+3)/(3)"
    },
    ...
  ]
}
```

This JSON file enables querying expressions with tools like [jq](https://jqlang.github.io/jq/).
For example:

- combinations using the digit `7` up to `100`, with a cost of `2`:

  ```sh
  onedigit 7 --max-value 100 --output-filename example.json
  cat example.json | jq '.combinations[] | select(.cost == 2)'
  ```

- sorted by cost and value:

  ```sh
  cat example.json | jq '.combinations | sort_by(.cost, .value)'
  ```

- showing only the value and expression:

  ```sh
  cat example.json | jq '.combinations[] | {"value":.value, "expression":.expr_full}'
  ```

- combinations not using factorial operation:

  ```sh
  cat example.json | jq '.combinations[] | select(.expr_full | contains("!") | not)'
  ```

## Development

Look at the [development guide](docs/development.md) for instructions on setting up a development environment, running tests, and contributing to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

木
