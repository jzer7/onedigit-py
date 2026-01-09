"""Single combination object."""

# Needed so classes can make self references to their type
from __future__ import annotations

import dataclasses
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
