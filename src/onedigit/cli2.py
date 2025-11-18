#!/usr/bin/env python3
"""CLI using argparse to calculate number combinations with a single digit."""

import argparse
import datetime
import json
from typing import Optional

from .logger import get_logger
from .simple import calculate

logger = get_logger(__name__)


def _create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="onedigit",
        description="Calculate number combinations with a single digit.",
        epilog="""
Examples:
  onedigit 3                      # Use digit 3 with defaults
  onedigit 7 --max-value 100      # Use digit 7, show values up to 100
  onedigit 5 --full               # Show full expressions instead of simple
  onedigit 3 --input input.json   # Load model from JSON file
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required positional argument
    parser.add_argument("digit", type=int, help="The digit to use to generate combinations (1-9)")

    # Optional arguments
    parser.add_argument(
        "--max-value",
        type=int,
        default=9999,
        help="Largest value for a combination to be shown in the output (default: 9999)",
    )

    parser.add_argument(
        "--max-cost",
        type=int,
        default=2,
        help="Maximum cost a combination can have for it to be remembered (default: 2)",
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="Maximum number of generative rounds (default: 5)",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Display combinations using full expressions instead of simple values",
    )

    parser.add_argument(
        "--input-filename",
        type=str,
        default="",
        help="JSON file used to preload the model",
    )

    parser.add_argument(
        "--output-filename",
        type=str,
        default="",
        help="JSON file used to store the model upon completion. If not provided, a random filename will be used",
    )

    return parser


def cmdline2(args: Optional[list[str]] = None) -> bool:
    """
    Main entry point for the argparse-based CLI.

    This function parses command line arguments, validates them,
    and calls the internal main function to perform the calculation.

    Args:
        args: Command line arguments (if None, uses sys.argv)

    Returns:
        bool: True if calculation runs without issues, False otherwise
    """
    parser = _create_parser()

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as e:
        # argparse calls sys.exit() on error, we catch it to return False
        return e.code == 0

    digit = parsed_args.digit

    # Set default values for arguments not provided
    max_value = parsed_args.max_value if parsed_args.max_value is not None else 9999
    max_cost = parsed_args.max_cost if parsed_args.max_cost is not None else 2
    max_steps = parsed_args.max_steps if parsed_args.max_steps is not None else 5
    input_filename = parsed_args.input_filename or ""
    output_filename = parsed_args.output_filename or ""

    # ------------------------------------------------------------
    # Input validation and sanitization
    try:
        digit = int(digit)
        max_value = int(max_value)
        max_cost = int(max_cost)
        max_steps = int(max_steps)
    except (ValueError, TypeError):
        logger.error("digit, max_value, max_cost, and max_steps must be positive integer numbers")
        return False

    if not (1 <= digit <= 9):
        logger.error("digit must be an integer number between 1 and 9")
        return False

    if not (1 <= max_value <= 1_000_000):
        logger.error("max_value must be a positive number between 1 and 1,000,000")
        return False

    if not (1 <= max_cost <= 30):
        logger.error("max_cost must be a positive number between 1 and 30")
        return False

    if not (1 <= max_steps <= 100):
        logger.error("max_steps must be a positive number between 1 and 100")
        return False

    if not isinstance(input_filename, str):
        logger.error("input_filename is not valid")
        return False

    if not isinstance(output_filename, str):
        logger.error("output_filename is not valid")
        return False

    # Call the (internal) main function with parsed arguments
    return _main(
        digit=parsed_args.digit,
        max_value=max_value,
        max_cost=max_cost,
        max_steps=max_steps,
        full=parsed_args.full,
        input_filename=input_filename,
        output_filename=output_filename,
    )


def _main(
    digit: int,
    max_value: int,
    max_cost: int,
    max_steps: int,
    full: bool,
    input_filename: str,
    output_filename: str,
) -> bool:
    """
    Internal main function to perform the calculation.

    It receives already validated and sanitized arguments.

    Args:
        digit (int): the digit to use to generate combinations.
        max_value (int): largest value for a combination to be shown in the output.
        max_cost (int): maximum cost a combination can have for it to be remembered.
        max_steps (int): maximum number of generative rounds.
        full (bool): display combinations using full expressions.
        input_filename (str): JSON file used to preload the model.
        output_filename (str): JSON file used to store the model upon completion. If not filename is provided, a random filename will be used.

    Returns:
        bool: True if calculation runs without issues.
    """
    logger.debug(
        f"calculate(digit={type(digit).__name__}({digit}), "
        f"max_value={type(max_value).__name__}({max_value}), "
        f"max_steps={type(max_steps).__name__}({max_steps}), "
        f"max_cost={type(max_cost).__name__}({max_cost}), "
        f"input_filename={type(input_filename).__name__}({input_filename}), "
        f"output_filename={type(output_filename).__name__}({output_filename})"
    )

    # ------------------------------------------------------------
    if not output_filename:
        tz = datetime.UTC
        t = datetime.datetime.now(tz)
        output_filename = "model" + "." + t.strftime("%Y%m%d%H%M%S") + ".json"

        # ------------------------------------------------------------
        tz = datetime.UTC
        t = datetime.datetime.now(tz)
        output_filename = "model" + "." + t.strftime("%Y%m%d%H%M%S") + ".json"

    # ------------------------------------------------------------
    # Check if there is input data
    input_text = ""
    if input_filename:
        input_lines = []
        try:
            with open(input_filename, mode="r", encoding="utf-8") as input_fp:
                input_lines = input_fp.readlines()
        except FileNotFoundError:
            logger.error(f"The input file '{input_filename}' does not exist.")
            return False
        except PermissionError:
            logger.error(f"No permissions to open the input file '{input_filename}'.")
            return False
        except Exception:
            logger.error(f"Unknown error opening the input file '{input_filename}'.")
            return False

        if not input_lines:
            logger.error(f"failed to read input file '{input_filename}', simulation will use a fresh model.")
        else:
            input_text = "".join(input_lines)
        del input_lines

    # Start calculation
    model = calculate(
        digit=digit,
        max_value=max_value,
        max_cost=max_cost,
        max_steps=max_steps,
        input_json=input_text,
    )
    del input_text

    # ------------------------------------------------------------
    # Get the combinations
    combos = []
    if not model:
        logger.error("failure creating and running model")
        return False
    else:
        combos = sorted(model.state.values())

    # ------------------------------------------------------------
    # Take care of outputs
    if output_filename:
        # Represent model in JSON format
        model_dict = model.asdict()
        jsenc = json.JSONEncoder()
        jstxt = jsenc.encode(model_dict)

        # Write the whole model to a file
        try:
            with open(output_filename, mode="w", encoding="utf-8") as output_fp:
                output_fp.write(jstxt)
        except PermissionError:
            logger.error(f"failed to open output file '{output_filename}' in write mode.")
            return False
        except Exception:
            logger.error(f"Unknown error writing to output file '{output_filename}'.")
            return False

    # ------------------------------------------------------------
    # Output to terminal
    for c in combos:
        if full:
            print(f"{c.value:>4} = {c.expr_full:<70}   [{c.cost:>3}]")
        else:
            print(f"{c.value:>4} = {c.expr_simple:<15}   [{c.cost:>3}]")

    return True
