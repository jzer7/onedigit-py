import unittest

from hypothesis import given
from hypothesis import strategies as hst

import onedigit

# class Model:
#     digit: int
#     max_value: int
#     max_cost: int
#     state: dict[int, Combo]
#     logger: logging.Logger
#     def __init__(self, digit: int, max_value: int, max_cost: int, *, shallow: bool = False): ...


class Test_Model(unittest.TestCase):
    def check_model(self, model: onedigit.Model, digit: int) -> None:
        # Verify integrity of the object
        assert model is not None
        assert isinstance(model, onedigit.Model)

        # Verify integrity of the Model object
        assert isinstance(model.digit, int)
        assert model.digit == digit
        assert 1 <= model.digit <= 9

        self.check_model_state(model, digit)

    def check_model_state(self, model: onedigit.Model, digit: int) -> None:
        assert isinstance(model.state, dict)
        assert len(model.state) > 0

        # At least we should have a combination for the digit itself
        assert digit in model.state
        assert model.state[digit] is not None
        assert isinstance(model.state[digit], onedigit.Combo)
        assert model.state[digit].value == digit

    def model_match(self, model1: onedigit.Model, model2: onedigit.Model) -> bool:
        # But models should be from the same digit space
        assert model1.digit == model2.digit

        # Verify integrity of the objects
        self.check_model(model1, model1.digit)
        self.check_model(model2, model2.digit)

        return False

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_creation_good(self, digit: int) -> None:
        # Good digit
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        self.check_model(model1, digit)

    @given(digit=hst.integers(min_value=10))
    def test_model_creation_bad(self, digit: int) -> None:
        # Bad digit
        with self.assertRaises(expected_exception=ValueError):
            model1 = onedigit.Model(digit=digit)
            assert not model1

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_initial_population(self, digit: int) -> None:
        # Create a fresh model. Active values of up to 3 digits (999).
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=999, max_cost=4)
        self.check_model(model1, digit)

        # Model needs to have some initial values, for the digit, and each of the concatenations
        combos = model1.get_valid_combos()
        assert len(combos) == 3

        # Check each combo
        for c in combos:
            # It can only have the digit in question
            digits = [d for d in c.expr_full if d in "0123456789"]

            assert all([d == str(digit) for d in digits])

            # The cost must match the times the number appears
            assert c.cost == len(digits)

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_update(self, digit: int) -> None:
        # Create a fresh model
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)

        # Get 1 combination that exists in a fresh model
        combo1 = model1.state[digit]

        # Check state before operations
        initial_size = len(model1.state)

        # It should not have 'digit + digit' or 'digit+digit+digit'
        assert (2 * digit) not in model1.state
        assert (3 * digit) not in model1.state

        # Define a few combinations
        combo2 = combo1.binary_operation(combo1, "+")
        combo3 = combo1.binary_operation(combo2, "+")

        # Add those new combinations into the model
        # And ensure they are added properly
        model1.state_update(combo2)
        assert len(model1.state) == initial_size + 1
        assert (2 * digit) in model1.state

        model1.state_update(combo3)
        assert len(model1.state) == initial_size + 2
        assert (3 * digit) in model1.state

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_copy_basic(self, digit: int) -> None:
        # Create a fresh model and get one combination from it
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        combo1 = model1.state[digit]

        # add one extra combination (value = digit + digit)
        model1.state_update(combo1.binary_operation(combo1, "+"))

        # Get a copy and delete the original objects
        model2 = model1.copy()
        del model1.state
        del model1
        del combo1

        # Verify integrity of the copy, after we have deleted the original
        self.check_model(model2, digit)

        # Check the new combination exists
        assert (digit + digit) in model2.state

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_copy(self, digit: int) -> None:
        # Create a model, copy it, but keep the original too
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        model2 = model1.copy()

        # Verify integrity of the copy
        self.check_model(model2, digit)

        # Check model parameters are identical
        assert model1.digit == model2.digit
        assert model1.max_value == model2.max_value
        assert model1.max_cost == model2.max_cost

        # Check their state matches as well
        assert len(model1.state) == len(model2.state)

        for val in model1.state.keys():
            assert val in model1.state
            assert val == model1.state[val].value

            assert val in model2.state
            assert val == model2.state[val].value

    # For serialization
    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_to_dictionary(self, digit: int) -> None:
        # Create the dictionary of a model
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        dict1 = model1.asdict()

        # Verify dictionary
        assert dict1 is not None
        assert isinstance(dict1, dict)

        # Verify fields
        assert "digit" in dict1
        assert isinstance(dict1["digit"], int)
        assert dict1["digit"] == digit

        assert "max_value" in dict1
        assert isinstance(dict1["max_value"], int)
        assert "max_cost" in dict1
        assert isinstance(dict1["max_cost"], int)
        assert "combinations" in dict1
        assert isinstance(dict1["combinations"], list)
        assert len(dict1["combinations"]) >= 1

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_from_dictionary_basic(self, digit: int) -> None:
        # Create the dictionary of a model
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        dict1 = model1.asdict()
        # Delete the original object to identify missing info
        del model1.state
        del model1

        # Check we can reconstruct the object
        model2 = onedigit.Model.fromdict(dict1)
        assert model2 is not None

        # Verify the hydrated Model is valid
        self.check_model(model2, digit)

    @given(digit=hst.integers(min_value=1, max_value=9))
    def test_model_from_dictionary(self, digit: int) -> None:
        # Create the dictionary of a model
        model1 = onedigit.Model(digit=digit)
        model1.seed(max_value=99, max_cost=4)
        dict1 = model1.asdict()

        # Check we can reconstruct the object
        model2 = onedigit.Model.fromdict(dict1)
        assert model2 is not None

        # Verify the hydrated Model matches the original model
        self.model_match(model1, model2)

        # The reverse relationship must also be satisfied
        self.model_match(model2, model1)
