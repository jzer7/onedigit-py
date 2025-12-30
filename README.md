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

```txt
10 = 5 + 5
15 = 5 + 5 + 5
20 = 5 + 5 + 5 + 5
25 = 5 + 5 + 5 + 5 + 5
...
```

Expanding the operations to allow multiplication results in less costly solutions:

```txt
25 = 5 + 5 + 5 + 5 + 5

25 = 5 * 5
```

And adding subtraction and division can both generate smaller solutions, and generate numbers we couldn't produce before.

```txt
20 = 5 * 5 - 5
4 = 5 - 5/5
```

Many magazine versions of the game stop there.
But online puzzles tend to include more operations.
I have seen some with exponentiation (`^`), factorial (`!`) and square root (`sqrt`).
And some even allow concatenation of the digit (example use `3` to produce `33`, with a cost of 2).
Using those operations results in some expressions that look like mathematical versions of [Rube Goldberg machines](https://en.wikipedia.org/wiki/Rube_Goldberg_machine).

## Usage

Install the package with `pip` (or your preferred package manager):

```sh
pip install onedigit-py
```

The script `onedigit` is a CLI to the solver.
The syntax is:

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
./onedigit 3
```

Show combinations for digit 7 up to 100 and show full expressions:

```sh
./onedigit 7 --max-value 100 --full
```

We can output the combinations as a JSON file.
The JSON format is helpful as we can use [jq](https://jqlang.github.io/jq/) to run queries on the output.
For example, to generate all combinations with the digit `7` up to `100`, with a cost less than `3`:

```sh
onedigit 7 --max-value 100 --output-filename example.json
cat example.json | jq '.combinations[] | select(.cost <= 3) | {"value":.value, "expression":.expr_full}'
```

A JSON file can be used to seed a future run.
This is useful to snapshot progress when looking for combinations of large numbers.
For example, we can obtain high-quality combinations (low cost) for numbers up to `200`.
That will be relatively quick as we are limiting the value of numbers we retain.
Then use those numbers as a starting point to look for combinations of larger numbers.

```sh
./onedigit 3 --max-value 200 --max-steps 12 --max-cost 9 --output-filename snapshot_001.json
./onedigit 3 --max-value 1000 --input-filename snapshot_001.json --output-filename snapshot_002.json
```

The above example takes about `0.25s` to generate combinations up to `200` with a maximum cost of `9`, and about `0.2s` to extend that to `1000`.
Whereas trying to do `1000` directly with a maximum cost of `9` takes about `5s`.

木
