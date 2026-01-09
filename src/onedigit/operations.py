"""Pure functions for arithmetic operations on Combo objects."""

import math

from .combo import Combo


def unary_operation(combo1: Combo, op: str) -> Combo:
    """
    Apply an operation on a single number.

    This function can result in an invalid value, in which case the
    result is a Combo object that evaluates to zero.

    Operations produce a new Combo object.
    Operations do not modify the current object.

    Args:
        combo1 (Combo): the combination to apply the operation on.
        op (str): operation to run (!, sqrt).

    Note:
        To avoid immensely large operations, the factorial
        operation only works on numbers up to '20'.

            20! is 62-bits (~2 x 10^18)
            21! is 66-bits
            24! is 80-bits
            30! is 108-bits
            34! is 128-bits

        Since this is a legitimate operation, it will not
        raise an exception. Instead i will return an empty
        combination.

    Raises:
        ValueError: when receiving an invalid operation

    Returns:
        Combo: a new Combo object.
    """
    # Only use parenthesis for cases it helps (if expression has spaces)
    value1_expr_full = combo1.expr_full
    if " " in value1_expr_full:
        value1_expr_full = "(" + value1_expr_full + ")"

    match op:
        case "!":
            if (combo1.value < 0) or (combo1.value > 20):
                return Combo(value=0)
            rc_val = math.factorial(combo1.value)
            rc_expr_full = value1_expr_full + "!"
            rc_expr_simple = str(combo1.value) + "!"
        case "sqrt":
            if combo1.value < 0:
                # Prevent irrational values
                return Combo(value=0)
            rc_val = math.isqrt(combo1.value)
            if (rc_val * rc_val) != combo1.value:
                # Only allow expressions that result in exact integer values
                return Combo(value=0)
            rc_expr_full = "√(" + value1_expr_full + ")"
            rc_expr_simple = "√(" + str(combo1.value) + ")"
        case _:
            raise ValueError("bad operator:", op)

    return Combo(
        value=rc_val,
        cost=combo1.cost,
        expr_full=rc_expr_full,
        expr_simple=rc_expr_simple,
    )


def binary_operation(combo1: Combo, combo2: Combo, op: str) -> Combo:
    """
    Apply an operation with this combo and another one.

    This function can result in an invalid value, in which case the
    result is a Combo object that evaluates to zero.

    Operations produce a new Combo object.
    Operations do not modify the current object.

    Args:
        combo1 (Combo): first combination to use
        combo2 (Combo): second combination to use
        op (str): operation to perform between both combinations.
            Operations supported: addition(+), subtraction(-),
            multiplication(*), integer division(/), exponentiation(^)

    Note:
        To avoid immensely large operations, the exponent in the
        exponentiation operation is limited to '40'.

            9^20 is 64-bits (~1.2 x 10^19)
            9^40 is 127-bits (~1.4 x 10^38)

        Since this is a legitimate operation, it will not
        raise an exception. Instead i will return an empty
        combination.

    Raises:
        ValueError: when receiving an invalid operation

    Returns:
        Combo: the result of the operation, as a new Combo object.
    """
    cost = combo1.cost + combo2.cost

    # Only use parenthesis for cases it helps (if expression has spaces)
    value1_expr_full, value2_expr_full = combo1.expr_full, combo2.expr_full
    if " " in value1_expr_full:
        value1_expr_full = "(" + value1_expr_full + ")"
    if " " in value2_expr_full:
        value2_expr_full = "(" + value2_expr_full + ")"

    match op:
        case "+":
            rc_val = combo1.value + combo2.value
            rc_expr_full = f"{value1_expr_full} + {value2_expr_full}"
            rc_expr_simple = f"{combo1.value} + {combo2.value}"

        case "-":
            rc_val = combo1.value - combo2.value
            rc_expr_full = f"{value1_expr_full} - {value2_expr_full}"
            rc_expr_simple = f"{combo1.value} - {combo2.value}"

        case "*":
            rc_val = combo1.value * combo2.value
            rc_expr_full = f"{value1_expr_full} * {value2_expr_full}"
            rc_expr_simple = f"{combo1.value} * {combo2.value}"

        case "/":
            if combo1.value % combo2.value != 0:
                return Combo(value=0)

            rc_val = combo1.value // combo2.value
            rc_expr_full = f"{value1_expr_full} / {value2_expr_full}"
            rc_expr_simple = f"{combo1.value} / {combo2.value}"

        case "^":
            # Prevent immensely large operations
            if combo1.value < 0 or combo2.value > 40:
                return Combo(value=0)
            # Prevent irrational values
            if combo2.value < 0:
                return Combo(value=0)

            rc_val = combo1.value**combo2.value
            rc_expr_full = f"{value1_expr_full} ^ {value2_expr_full}"
            rc_expr_simple = f"{combo1.value} ^ {combo2.value}"

        case _:
            raise ValueError("bad operator:", op)

    return Combo(value=rc_val, cost=cost, expr_full=rc_expr_full, expr_simple=rc_expr_simple)
