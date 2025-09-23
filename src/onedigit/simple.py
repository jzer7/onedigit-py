"""Functionality for easy access. It schedules the operations that calculate the combinations."""

import json

import onedigit

from .logger import get_logger

logger = get_logger(__name__)


def calculate(
    digit: int, *, max_value: int = 9999, max_cost: int = 10, max_steps: int = 10, input_json: str
) -> onedigit.Model | None:
    """
    Run a simple calculation.

    Args:
        digit (int): digit to use
        max_value (int, optional): largest value to remember. Defaults to 9999.
        max_cost (int, optional): maximum cost a combination can have to be remembered. Defaults to 10.
        max_steps (int, optional): maximum number of steps (iterations) to run. Defaults to 10.
        input_json (str, optional): JSON model data. Defaults to empty.

    Returns:
        onedigit.Model: model object, or None if there is a failure.
    """
    logger.debug(f"calculate(digit={digit}, max_value={max_value}, max_cost={max_cost}, max_steps={max_steps})")

    mymodel = get_model(digit=digit, max_value=max_value, max_cost=max_cost, input_json=input_json)
    if not mymodel:
        return None

    mymodel = advance(mymodel=mymodel, max_steps=max_steps)
    if not mymodel:
        return None

    return mymodel


def get_model(digit: int, *, max_value: int = 9999, max_cost: int = 2, input_json: str = "") -> onedigit.Model | None:
    """
    Obtain an initial model.

    If valid JSON data is provided, the model is built from it.
    Otherwise a fresh model is created.

    Args:
        digit (int): digit to use
        max_value (int, optional): largest value to remember. Defaults to 9999.
        max_cost (int, optional): maximum cost a combination can have to be remembered. Defaults to 10.
        input_json (str, optional): JSON text that represents a model. Defaults to empty.

    Returns:
        onedigit.Model: a model, or None.
    """
    logger.debug(
        f"get_model(digit={digit}, max_value={max_value}, max_cost={max_cost}, input_json={len(input_json)} chars)"
    )
    # Build a blank model
    mymodel = onedigit.Model(digit=digit)

    # Parse the input JSON
    if mymodel and input_json:
        json_dec = json.JSONDecoder()
        input_dict = json_dec.decode(input_json)

        if input_dict:
            # Ingest the actual dictionary
            try:
                mymodel2 = onedigit.Model.fromdict(input=input_dict)
            except ValueError as e:
                logger.error("failed to import model:", e)
        if mymodel2.digit == digit:
            mymodel = mymodel2
        else:
            logger.error(f"requested model for digit={digit}, ignoring imported model as it has digit={mymodel2.digit}")

    if not mymodel:
        logger.error("unable to build a model")
        return None

    # Adjust parameters and add initial values (in case they do not exist there already)
    mymodel.seed(max_value=max_value, max_cost=max_cost)

    return mymodel


def advance(mymodel: onedigit.Model, max_steps: int = 10) -> onedigit.Model:
    """
    Perform iterations over a onedigit model.

    This function will stop earlier than the number of steps,
    if there is no change in state after an iteration.

    Args:
        mymodel (onedigit.Model): model at the begining of the simulation.
        max_steps (int): maximum number of steps (iterations) to run. Defaults to 10.

    Returns:
        onedigit.Model: reference to the updated model.
    """
    logger.debug(f"simple.advance(mymodel={mymodel}, max_steps={max_steps})")

    # Run a few steps
    for step in range(1, max_steps + 1):
        updates = mymodel.simulate()
        if updates == 0:
            logger.info(f"stopping early as state does not advance past {step} iterations.")
            break
        else:
            logger.info(f"iteration {step} found {updates} new combinations.")

    return mymodel
