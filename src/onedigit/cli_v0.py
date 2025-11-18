#!/usr/bin/env python3
"""CLI to calculate number combinations with a single digit."""

import datetime
import json

from .logger import get_logger
from .simple import calculate

logger = get_logger(__name__)


def app_old(
    digit: int,
    *,
    max_value: int = 9999,
    max_cost: int = 2,
    max_steps: int = 5,
    full: bool = False,
    input_filename: str = "",
    output_filename: str = "",
) -> bool:
    """
    Command line interface to calculate combinations using a given digit.

    The only value required is 'digit'. All other arguments have default values.

    The input file is a JSON file that describes a model. It can also have results from a previous simulation.

    WARNING: The JSON file must correspond to a model with the same value of 'digit' as the one specified in the command line.

    Args:
        digit (int): the digit to use to generate combinations.
        max_value (int, optional): largest value for a combination to be shown in the output. Defaults to 9999.
        max_cost (int, optional): maximum cost a combination can have for it to be remembered. Defaults to 2.
        max_steps (int, optional): maximum number of generative rounds. Defaults to 5.
        full (bool, optional): display combinations using full expressions. Defaults to False.
        input_filename (str, optional): JSON file used to preload the model. Empty by default.
        output_filename (str, optional): JSON file used to store the model upon completion. If not filename is provided, a random filename will be used. Empty by default.

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
    # This is an entry level function. So handle for input
    # sanitation.
    try:
        digit = int(digit)
        max_value = int(max_value)
        max_cost = int(max_cost)
        max_steps = int(max_steps)
    except ValueError:
        logger.error("digit, max_value, max_cost, and max_steps must be positive integer numbers")
        return False

    if not (1 <= digit <= 9):
        logger.error("digit must be an integer number between 1 and 9")
        return False

    # ------------------------------------------------------------
    if not isinstance(input_filename, str):
        logger.error("input_filename is not valid")  # type: ignore

    if not isinstance(output_filename, str):
        logger.error("output_filename is not valid")  # type: ignore
    if not output_filename:
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
        except PermissionError:
            logger.error(f"No permissions to open the input file '{input_filename}'.")
        except ValueError:
            logger.error(f"Unknown error opening the input file '{input_filename}'.")

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

    # ------------------------------------------------------------
    # Output to terminal
    for c in combos:
        if full:
            print(f"{c.value:>4} = {c.expr_full:<70}   [{c.cost:>3}]")
        else:
            print(f"{c.value:>4} = {c.expr_simple:<15}   [{c.cost:>3}]")

    return True
