"""Single combination object."""

# Needed so classes can make self references to their type
from __future__ import annotations

import dataclasses
import math
from typing import Any

from .logger import get_logger

logger = get_logger(__name__)


@dataclasses.dataclass
class Combo:
    """
    Represents an arithmetic combination using a single digit.

    Args:
        value (int): value of the expression after evaluation.
        cost (int): number of times the digit is used in the expression.
        expr_full (str): string representing the instruction.
        expr_simple (str): string representing a simplified expression
            of the last value(s) and operand that were used to generate
            this expression.
    """

    value: int
    cost: int = 0  # (set to 10**9 if empty)
    expr_full: str = ""  # (set to str(value) if empty)
    expr_simple: str = ""  # (set to str(value) if empty)

    def __post_init__(self) -> None:
        """Run after instantiation of a dataclass object."""
        if self.cost == 0:
            self.cost = 10**9
        if not self.expr_full:
            self.expr_full = str(self.value)
        if not self.expr_simple:
            self.expr_simple = str(self.value)

    def __repr__(self) -> str:
        """
        Provide a string representation of the Combo object.

        Returns:
            str: string representation of the Combo object
        """
        return f"Combo: {self.value} = {self.expr_simple}    [{self.cost}]"

    def __lt__(self, other: Combo) -> bool:
        """
        Compare the order of this combination against another.

        This function is used by Python to sort containers
        with this type of objects.

        Args:
            other (Combo): combination object we are comparing with

        Returns:
            bool: True if this combination has a lower value compared to the 'other' combination.
        """
        if not isinstance(other, Combo):
            raise ValueError(f"Combo '__lt__' is undefined for type{type(other)}.")
        return self.value < other.value

    @classmethod
    def fromdict(cls, input: dict[str, Any]) -> Combo:
        """
        Create a Combo object from a dictionary.

        Functions to export an Model to a dictionary, and to create an
        object from a dictionary are used during object serialization. That
        functionality is used when taking snapshots of a Model simulation.

        Args:
            input (dict): dictionary representation of the object

        Raises:
            ValueError: when the input dictionary is not valid.
        """
        # Keys with integer values
        for k in ["value", "cost"]:
            if k not in input:
                raise ValueError(f"input dictionary is missing key '{k}'")
            v = input[k]
            if not isinstance(v, int):
                raise ValueError(f"value associated with key '{k}' must be an integer, but is '{type(v).__name__}'")

        # Keys with string values
        for k in ["expr_full", "expr_simple"]:
            if k not in input:
                raise ValueError(f"input dictionary is missing key '{k}'")
            v = input[k]
            if not isinstance(v, str):
                raise ValueError(f"value associated with key '{k}' must be a string, but is '{type(v).__name__}'")

        value = input["value"]
        cost = input["cost"]
        expr_full = input["expr_full"]
        expr_simple = input["expr_simple"]

        return Combo(value=value, cost=cost, expr_full=expr_full, expr_simple=expr_simple)

    def asdict(self) -> dict[str, Any]:
        """
        Create a dictionary representation of the Combo object.

        This is needed to serialize the object to JSON.
        It is also used during serialization of the Model object
        (see Model.asdict()).

        Returns:
            dict[str, Any]: dictionary with the dataclass fields.
        """
        return dataclasses.asdict(self)

    def unary_operation(self, op: str) -> Combo:
        """
        Apply an operation on a single number.

        This function can result in an invalid value, in which case the
        result is a Combo object that evaluates to zero.

        Operations produce a new Combo object.
        Operations do not modify the current object.

        Args:
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
        value1_expr_full = self.expr_full
        if " " in value1_expr_full:
            value1_expr_full = "(" + value1_expr_full + ")"

        match op:
            case "!":
                if (self.value < 0) or (self.value > 20):
                    return Combo(value=0)
                rc_val = math.factorial(self.value)
                rc_expr_full = value1_expr_full + "!"
                rc_expr_simple = str(self.value) + "!"
            case "sqrt":
                if self.value < 0:
                    # Prevent irrational values
                    return Combo(value=0)
                rc_val = math.isqrt(self.value)
                if (rc_val * rc_val) != self.value:
                    # Only allow expressions that result in exact integer values
                    return Combo(value=0)
                rc_expr_full = "√(" + value1_expr_full + ")"
                rc_expr_simple = "√(" + str(self.value) + ")"
            case _:
                raise ValueError("bad operator:", op)

        return Combo(
            value=rc_val,
            cost=self.cost,
            expr_full=rc_expr_full,
            expr_simple=rc_expr_simple,
        )

    def binary_operation(self, combo2: Combo, op: str) -> Combo:
        """
        Apply an operation with this combo and another one.

        This function can result in an invalid value, in which case the
        result is a Combo object that evaluates to zero.

        Operations produce a new Combo object.
        Operations do not modify the current object.

        Args:
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
        cost = self.cost + combo2.cost

        # Only use parenthesis for cases it helps (if expression has spaces)
        value1_expr_full, value2_expr_full = self.expr_full, combo2.expr_full
        if " " in value1_expr_full:
            value1_expr_full = "(" + value1_expr_full + ")"
        if " " in value2_expr_full:
            value2_expr_full = "(" + value2_expr_full + ")"

        match op:
            case "+":
                rc_val = self.value + combo2.value
                rc_expr_full = f"{value1_expr_full} + {value2_expr_full}"
                rc_expr_simple = f"{self.value} + {combo2.value}"

            case "-":
                rc_val = self.value - combo2.value
                rc_expr_full = f"{value1_expr_full} - {value2_expr_full}"
                rc_expr_simple = f"{self.value} - {combo2.value}"

            case "*":
                rc_val = self.value * combo2.value
                rc_expr_full = f"{value1_expr_full} * {value2_expr_full}"
                rc_expr_simple = f"{self.value} * {combo2.value}"

            case "/":
                if self.value % combo2.value != 0:
                    return Combo(value=0)

                rc_val = self.value // combo2.value
                rc_expr_full = f"{value1_expr_full} / {value2_expr_full}"
                rc_expr_simple = f"{self.value} / {combo2.value}"

            case "^":
                # Prevent immensely large operations
                if self.value < 0 or combo2.value > 40:
                    return Combo(value=0)
                # Prevent irrational values
                if combo2.value < 0:
                    return Combo(value=0)

                rc_val = self.value**combo2.value
                rc_expr_full = f"{value1_expr_full} ^ {value2_expr_full}"
                rc_expr_simple = f"{self.value} ^ {combo2.value}"

            case _:
                raise ValueError("bad operator:", op)

        return Combo(value=rc_val, cost=cost, expr_full=rc_expr_full, expr_simple=rc_expr_simple)
