# Single Digit Combinations

This is a number puzzle I saw in a newspaper when I was a kid.
I do not know the official name of the game,
but its objective is to find the _smallest expression_ that produces a value using a single digit.

## Background

It is easier to understand this by looking at a problem.
Say we are asked to find combinations to produce the number `75`.
A simple case is using the digit `3`.

1. The number `75` is divisible by `3`, so we would think `3 * 25`, except we cannot use `25`.
1. So now we need to look for an expression that evaluates to `25`. A good option could be `27 - 2`.
1. The first term is simply `3 ^ 3`.
1. Now we need an expression that produces `2` in terms of `3`. We could use `3 - 1`.
1. And use `3 / 3` to produce that `1`.

So a valid combination would be $(3 \times (3^3 - (3 - \frac{3}{3})))$.

Continuing with this example, we can try another digit, say `6`.
Notice that `6 * 12` is `72`, which gets us closer to the target.
So we can think of `75` as `72 + 3`.
The first term (`72`) is easy (`6 * 12`), but getting the second term, `3`, requires some creative thinking.
Eventually we end up with something like $(6 \times (6 + 6) + \frac{6 \times 6}{6 + 6})$.

### Scoring

The cost of a solution is determined by the number of times the digit is used.
So the solution $(3 \times (3^3 - (3 - \frac{3}{3})))$, has a cost of `6`.
Likewise, the solution using the digit `6` has a cost of `7`.

We can improve both solutions.
One solution for the digit `3` would be $(3 \times 3^3 - 3!)$, which is `81 - 6`, and has a cost of `4`.
And an improvement on the solution with the digit `6` could be $(\frac{666}{6} - 6 \times 6)$, with a cost of `6`.

### Operations

The operations allowed also impact the difficulty of the game.
Allowing only additions is the most limiting case.
It makes for an easy game without much challenge.
For example, using the digit `5`, we can only do:

```
10 = 5 + 5
15 = 5 + 5 + 5
20 = 5 + 5 + 5 + 5
25 = 5 + 5 + 5 + 5 + 5
...
```

Expanding the operations to allow multiplication results in less costly solutions:

```
25 = 5 + 5 + 5 + 5 + 5

25 = 5 * 5
```

And adding subtraction and division can both generate smaller solutions, and generate numbers we couldn't produce before.

```
20 = 5 * 5 - 5
4 = 5 - 5/5
```

Many magazine versions of the game stop there.
But online puzzles tend to include more operations.
I have seen some with exponentiation (`^`), factorial (`!`) and square root (`sqrt`).
And some even allow concatenation of the digit (example use `3` to produce `33`, with a cost of 2).
Using those operations results in some expressions that look like mathematical versions of [Rube Goldberg machines](https://en.wikipedia.org/wiki/Rube_Goldberg_machine).

## Solver

For the solver, I am using monotonic operations at first.
That allows us to have a _directed acyclic graph_ (DAG).

To get past the first limitation, I will also allow the use of the number `1` at cost of 2 (the result of `5/5`).

## Usage

The script `onedigit` is a CLI to the solver.
The syntax is:

```txt
onedigit [OPTIONS]

Options:
  --digit <number>              digit to use for expressions
  --max_value <number>          largest number to report
  --max_steps <number>          number of iterations
  --max_cost <number>           largest cost for an expression to be used
  --full                        show combinations in terms of the digit, otherwise use expanded values
  --input_filename <filename>   import a JSON file that describes the model
  --output_filename <filename>  name of a JSON used for the output, an automatic name would be used otherwise.
  --help                        this information
```

### Examples

The simplest use is to get combinations using the digit `3`.

```sh
onedigit --digit 3
```

To see the default values:

```sh
onedigit --help
```

The JSON format is helpful as we can use [jq](https://jqlang.github.io/jq/) to run queries on the output.
For example, to generate all combinations with the digit `7` up to `100`, with a cost less than '3'.

```sh
onedigit --digit 7 --max_value 100 --output_filename foo.json
cat foo.json | jq '.[] | select(.cost <= 3) | {"value":.value, "expression":.expr_full}'
```

## Alternative CLI (cli2.py)

This project also includes an alternative CLI implementation (`cli2.py`) that uses Python's `argparse` instead of the `fire` library. This provides a more traditional command-line interface experience.

### Usage

The script `onedigit2` provides the same functionality as `onedigit` but with standard argparse-style arguments:

```txt
usage: onedigit [-h] [--max-value MAX_VALUE] [--max-cost MAX_COST] 
                [--max-steps MAX_STEPS] [--full] [--input-filename INPUT_FILENAME] 
                [--output-filename OUTPUT_FILENAME] digit

Calculate number combinations with a single digit.

positional arguments:
  digit                 The digit to use to generate combinations (1-9)

options:
  -h, --help            show this help message and exit
  --max-value MAX_VALUE
                        Largest value for a combination to be shown in the output (default: 9999)
  --max-cost MAX_COST   Maximum cost a combination can have for it to be remembered (default: 2)
  --max-steps MAX_STEPS
                        Maximum number of generative rounds (default: 5)
  --full                Display combinations using full expressions instead of simple values
  --input-filename INPUT_FILENAME
                        JSON file used to preload the model
  --output-filename OUTPUT_FILENAME
                        JSON file used to store the model upon completion
```

### Examples

The simplest use is to get combinations using the digit `3`:

```sh
./onedigit2 3
```

Show combinations for digit 7 up to 100 with full expressions:

```sh
./onedigit2 7 --max-value 100 --full
```

Load model from file and save results:

```sh
./onedigit2 3 --input-filename input.json --output-filename results.json
```

Both CLI implementations (`onedigit` and `onedigit2`) produce identical results and support the same functionality.

木
