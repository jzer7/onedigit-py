"""Single digit model object."""

# Needed so classes can make self references to their type
from __future__ import annotations

from typing import Any, List

from .combo import Combo
from .logger import get_logger
from .operations import binary_operation, unary_operation

logger = get_logger(__name__)


class Model:
    """Model the space for expressions using a single digit."""

    digit: int
    max_value: int = 0
    max_cost: int = 0
    state: dict[int, Combo]

    def __init__(self, digit: int) -> None:
        """
        Build a model for the game simulation.

        Args:
            digit (int): digit to use when creating expressions

        Raises:
            ValueError: if digit value is out of range [1,9]
        """
        logger.debug("Model.__init__()")

        if not isinstance(digit, int) or not (1 <= digit <= 9):
            raise ValueError("digit must be an integer between 1 and 9, inclusive.")
        self.digit = digit

        self.state = {}

    def seed(self, *, max_value: int = 0, max_cost: int = 0) -> None:
        """
        Create initial combinations for the model.

        Args:
            max_value (int, optional): upper limit of values the model
                retains.
            max_cost (int, optional): maximum cost a combination can
                have, for the simulation to use it to generate other
                combinations.

        Raises:
            ValueError: if max value is too large (more than 1M).
        """
        if not isinstance(max_value, int) or not (1 <= max_value <= 1_000_000):
            raise ValueError("max value must be a positive number below 1M.")
        self.max_value = max_value

        if not isinstance(max_cost, int) or not (1 <= max_cost <= 30):
            raise ValueError("maximum cost must be a positive number below 30.")
        self.max_cost = max_cost

        # Set up the digit for the simulation
        self.state[self.digit] = Combo(
            value=self.digit,
            cost=1,
            expr_full=str(self.digit),
            expr_simple=str(self.digit),
        )

        # Allow expressions for joint digits (say, 22, two 2s)
        if 1 <= self.digit <= 9:
            num, expr, cost = self.digit, str(self.digit), 1
            while (num <= self.max_value) and (cost <= self.max_cost):
                self.state[num] = Combo(value=num, cost=cost, expr_full=expr, expr_simple=expr)

                num, expr, cost = (
                    10 * num + self.digit,
                    expr + str(self.digit),
                    cost + 1,
                )

    def copy(self) -> Model:
        """
        Create a new object with all information about this model.

        This function is used as a way to create a snapshot. When called
        a blank Model object is created, and data from the current object
        is copied over. At the end, there are no data structures shared
        between both objects.

        Returns:
            Model: a new Model object
        """
        new_model = Model(digit=self.digit)
        new_model.digit = self.digit
        new_model.max_value = self.max_value
        new_model.max_cost = self.max_cost
        new_model.state = self.state.copy()
        return new_model

    @classmethod
    def fromdict(cls, input: dict[str, Any]) -> Model:
        """
        Create a Model object from a dictionary.

        Functions to export an Model to a dictionary, and to create an
        object from a dictionary are used during object serialization. That
        functionality is used when taking snapshots of a Model simulation.

        Args:
            input (dict): dictionary representation of the object

        Raises:
            ValueError: when the input dictionary is not valid.
        """
        for k in ["digit", "max_value", "max_cost", "combinations"]:
            if k not in input:
                raise ValueError(f"input dictionary is missing key {k}")

        new_model = Model(digit=input["digit"])
        new_model.digit = input["digit"]
        new_model.max_value = input["max_value"]
        new_model.max_cost = input["max_cost"]
        new_model.state = {}

        state = {}
        for cdict in input["combinations"]:
            combo = Combo.fromdict(cdict)
            state[combo.value] = combo

        new_model.state = state

        return new_model

    def __repr__(self) -> str:
        """
        Provide a string representation of the Model object.

        Returns:
            str: string representation of the Model object
        """
        return f"Model(digit={self.digit}, max_value={self.max_value}, max_cost={self.max_cost})"

    def state_update(self, candidate: Combo) -> bool:
        """
        Attempt addition of a single combination to the existing state.

        The combination will be checked against existing solutions, and
        it will be added if it is consider beneficial to the calculation.

        Args:
            candidate (Combo): combination to add

        Returns:
            bool: True if the update was valid.
        """
        # logger.debug("Model.state_update()")

        if candidate.cost > self.max_cost:
            return False

        value, cost = candidate.value, candidate.cost

        # Are we keeping track of this value?
        if not (1 <= value <= self.max_value):
            return False

        # There was no improvement in cost
        if (value in self.state) and (self.state[value].cost <= cost):
            return False

        self.state[value] = candidate
        return True

    def state_merge(self, extra: Model) -> None:
        """
        Merge combinations from a separate Model into the current model.

        It picks the best combination for a given value based on cost of
        the full expression.

        Args:
            extra (Model): model with combinations to be added to this model
        """
        logger.debug("Model.state_merge()")

        for combo2 in extra.get_valid_combos():
            val2, cost2 = combo2.value, combo2.cost

            if (
                cost2 <= self.max_cost
                and val2 >= 1
                and val2 <= self.max_value
                and (val2 not in self.state or cost2 < self.state[val2].cost)
            ):
                self.state[val2] = combo2

    def simulate(self) -> int:
        """
        Run one round of the simulation.

        The function takes all existing combinations, and applies
        operations that generate new values, and stores them in a
        separate object. Once all initial values are processed, we
        merge combinations from the new object. That prevents recursive
        loops, and let us determine liveness.

        Returns:
            int: number of values that were updated
        """
        known = list(self.state.values())
        known.sort(key=lambda c: c.value)
        new_combos = self.copy()

        updates = 0
        for combo1 in known:
            # Unary operations
            #   !:    factorial
            #   sqrt: square root
            for op in ["!", "sqrt"]:
                updates += new_combos.state_update(unary_operation(combo1, op=op))

            for combo2 in known:
                # We only run cases where combo1 >= combo2
                #   + and * are commutative
                #   / and - are not commutative, but problem deals with
                #           positive integers, so it does not make sense
                #           to run cases where combo1 < combo2
                for op in ["+", "-", "*", "/"]:
                    if combo1.value >= combo2.value:
                        updates += new_combos.state_update(binary_operation(combo1, combo2, op))

                # We need to run both cases (combo1 > combo2, and combo2 > combo1)
                #   ^
                for op in ["^"]:
                    updates += new_combos.state_update(binary_operation(combo1, combo2, op))

        self.state_merge(new_combos)

        return updates

    def get_valid_combos(self) -> List[Combo]:
        """
        Get valid combinations.

        Returns:
            List[Combo]: list of valid Combo objects
        """
        return list(self.state.values())

    def asdict(self) -> dict[str, Any]:
        """
        Create a dictionary representation of the Model object.

        Functions to export an Model to a dictionary, and to create an
        object from a dictionary are used during object serialization. That
        functionality is used when taking snapshots of a Model simulation.

        Returns:
            dict[str, Any]: dictionary with the dataclass fields.
        """
        state = []
        for num in sorted(self.state.keys()):
            state.append(self.state[num].asdict())

        obj = {
            "digit": self.digit,
            "max_cost": self.max_cost,
            "max_value": self.max_value,
            "combinations": state,
        }
        return obj
