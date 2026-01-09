import math
import re
import unittest

from hypothesis import given
from hypothesis import strategies as hst

from onedigit.combo import Combo
from onedigit.operations import binary_operation, unary_operation

# For an explanation of the Combo class, look at `docs/solver.md#combo-representation`.


class Test_Combo(unittest.TestCase):
    def combination_to_python_expression(self, expr: str) -> str:
        """
        Converts custom mathematical notation to Python-evaluable syntax:
        - ^ (exponentiation) -> **
        - / (integer division) -> //
        - √ (square root) -> math.isqrt
        - ! (factorial, postfix) -> math.factorial

        Args:
            expr: Expression string using custom notation
        Returns:
            Converted expression string suitable for Python eval()
        """
        # Convert custom operators to Python syntax
        expr_mod = expr.replace("^", "**")
        expr_mod = expr_mod.replace("/", "//")
        expr_mod = expr_mod.replace("√", "math.isqrt")

        # Handle factorial (postfix notation): convert "expr!" to "math.factorial(expr)"
        # First handle parenthesized expressions: (expr)! -> math.factorial(expr)
        expr_mod = re.sub(r"\(([^)]+)\)!", r"math.factorial(\1)", expr_mod)
        # Then handle simple numbers: 5! -> math.factorial(5)
        expr_mod = re.sub(r"(\d+)!", r"math.factorial(\1)", expr_mod)

        return expr_mod

    def check_expression(self, expr: str, expect: int) -> None:
        """
        Validate that a Python arithmetic expression evaluates to the expected value.

        The evaluation uses a restricted namespace for safety.

        Args:
            expr: Expression string using custom notation
            expect: Expected integer result after evaluation

        Raises:
            AssertionError: If expression fails to evaluate or result doesn't match expected value
        """
        try:
            # Note: Using eval() here is acceptable for test code with controlled input.
            result = eval(expr, {"__builtins__": {}}, {"math": math})  # nosec B307
        except Exception as e:
            raise AssertionError(f"Expression '{expr}' failed to evaluate: {e}")

        # Verify result is an integer matching expected value
        assert isinstance(result, (int, float)), f"Result {result} is not numeric"
        if isinstance(result, float):
            assert result.is_integer(), f"Result {result} is not an integer value"
            result = int(result)

        assert result == expect, f"Expression '{expr}' evaluated to {result}, expected {expect}"

    def check_combo(self, combo_obj: Combo, target_value: int) -> None:
        """
        Verify integrity of a Combo object.

        Args:
            combo_obj: The Combo object to validate
            target_value: Expected value of the combo and its expressions

        Raises:
            AssertionError: If any validation check fails
        """
        # Verify the computed value matches expected
        assert combo_obj.value == target_value

        # Verify both expression formats evaluate to the target value
        py_expr_full = self.combination_to_python_expression(combo_obj.expr_full)
        py_expr_simple = self.combination_to_python_expression(combo_obj.expr_simple)

        self.check_expression(py_expr_full, target_value)
        self.check_expression(py_expr_simple, target_value)

        # HACK: combo_obj is a new object, as such its cost should be high.
        # This check should really be done by the caller of this method.
        assert combo_obj.cost > 1000

    @given(value1=hst.integers())
    def test_combo_positional(self, value1: int) -> None:
        combo1 = Combo(value1)
        self.check_combo(combo1, value1)

    # For serialization
    @given(value=hst.integers(min_value=1), cost=hst.integers(min_value=1))
    def test_combo_to_dictionary(self, value: int, cost: int) -> None:
        # Create a simple combo, and get its dictionary
        combo1 = Combo(value=value, cost=cost, expr_full=str(value), expr_simple=str(value))
        dict1 = combo1.asdict()

        # Verify dictionary
        assert dict1 is not None
        assert isinstance(dict1, dict)

        # Verify fields
        assert "value" in dict1
        assert isinstance(dict1["value"], int)
        assert dict1["value"] == value

        assert "cost" in dict1
        assert isinstance(dict1["cost"], int)
        assert dict1["cost"] == cost

        assert "expr_full" in dict1
        assert isinstance(dict1["expr_full"], str)
        assert dict1["expr_full"] == str(value)

        assert "expr_simple" in dict1
        assert isinstance(dict1["expr_simple"], str)
        assert dict1["expr_simple"] == str(value)

    @given(value1=hst.integers())
    def test_combo_repr(self, value1: int) -> None:
        combo1 = Combo(value1)

        str1 = str(combo1)

        assert str1

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_ordering(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        if value1 > value2:
            assert combo1 > combo2
            assert combo2 < combo1

        if value2 > value1:
            assert combo1 < combo2
            assert combo2 > combo1

        if value2 == value1:
            assert not (combo1 < combo2)
            assert not (combo1 > combo2)

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_addition(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        combo3 = binary_operation(combo1, combo2, "+")
        combo4 = binary_operation(combo2, combo1, "+")

        self.check_combo(combo3, value1 + value2)
        self.check_combo(combo4, value2 + value1)

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_subtraction(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        combo3 = binary_operation(combo1, combo2, "-")
        combo4 = binary_operation(combo2, combo1, "-")

        self.check_combo(combo3, value1 - value2)
        self.check_combo(combo4, value2 - value1)

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_multiplication(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        combo3 = binary_operation(combo1, combo2, "*")
        combo4 = binary_operation(combo2, combo1, "*")

        self.check_combo(combo3, value1 * value2)
        self.check_combo(combo4, value2 * value1)

    @given(value1=hst.integers())
    def test_combo_integer_division_by_zero(self, value1: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(0)

        with self.assertRaises(expected_exception=ZeroDivisionError):
            combo3 = binary_operation(combo1, combo2, "/")
            assert combo3.value == 0

    @given(value1=hst.integers(min_value=1))
    def test_combo_integer_division_by_one(self, value1: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value1)

        combo3 = binary_operation(combo1, combo1, "/")
        combo4 = binary_operation(combo1, combo2, "/")

        self.check_combo(combo3, 1)
        self.check_combo(combo4, 1)

    @given(value1=hst.integers(min_value=1), value2=hst.integers(min_value=1))
    def test_combo_integer_division(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        combo3 = binary_operation(combo1, combo2, "/")
        combo4 = binary_operation(combo2, combo1, "/")

        if (value1 % value2) == 0:
            self.check_combo(combo3, value1 // value2)
        else:
            self.check_combo(combo3, 0)

        if value2 % value1 == 0:
            self.check_combo(combo4, value2 // value1)
        else:
            self.check_combo(combo4, 0)

    @given(value1=hst.integers(min_value=1), value2=hst.integers(min_value=0, max_value=50))
    def test_combo_integer_exponentiation(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        # The object method protects against gigantic values.
        combo3 = binary_operation(combo1, combo2, "^")

        # But we also need to protect the tester from crashing
        # while evaluating that exponentiation.
        if (value1 < 0) or (value2 > 40):
            self.check_combo(combo3, 0)
            return

        self.check_combo(combo3, (value1**value2))

    @given(value1=hst.integers(min_value=1), value2=hst.integers(max_value=-1))
    def test_combo_integer_exponentiation_negative_exponent(self, value1: int, value2: int) -> None:
        combo1 = Combo(value1)
        combo2 = Combo(value2)

        combo3 = binary_operation(combo1, combo2, "^")

        # Negative exponents are not allowed, thus result should be zero
        self.check_combo(combo3, 0)

    @given(value1=hst.integers())
    def test_combo_sqrt(self, value1: int) -> None:
        combo1 = Combo(value1)

        combo2 = unary_operation(combo1, "sqrt")

        # Should not allow negative numbers
        if value1 < 0:
            self.check_combo(combo2, 0)
            return

        # Should only allow square numbers
        expected1 = math.isqrt(value1)
        if expected1 * expected1 != value1:
            expected1 = 0

        self.check_combo(combo2, expected1)

    @given(value1=hst.integers(max_value=50))
    def test_combo_factorial(self, value1: int) -> None:
        combo1 = Combo(value1)

        # The object method protects against gigantic values.
        combo2 = unary_operation(combo1, "!")

        # But we also need to protect the tester from crashing
        # while evaluating that factorial.
        if (value1 < 0) or (value1 > 20):
            self.check_combo(combo2, 0)
            return

        self.check_combo(combo2, math.factorial(value1))
