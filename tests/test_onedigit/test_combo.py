import math
import unittest

from hypothesis import given
from hypothesis import strategies as hst

import onedigit

# class Combo:
#     value: int
#     cost: int = 0  # (set to 10**9 if empty)
#     expr_full: str = ""  # (set to str(value) if empty)
#     expr_simple: str = ""  # (set to str(value) if empty)


class Test_Combo(unittest.TestCase):
    def check_expression(self, expr: str, expect: int) -> None:
        # Expression must evaluate to the expected value

        # Handle integer exponentiation
        expr2 = expr.replace("^", "**")

        # TODO: need to handle integer division in a cleaner way
        expr3 = expr2.replace("/", "//")

        # TODO: need to handle square root in a cleaner way
        expr4 = expr3.replace("√", "math.isqrt")

        # FIXME: need to handle factorial
        result = eval(expr4)

        assert result == expect

    def check_combo(self, combo1: onedigit.Combo, value1: int) -> None:
        # Verify integrity of the object
        assert combo1.value == value1
        assert combo1.cost > 1000
        self.check_expression(combo1.expr_full, value1)
        self.check_expression(combo1.expr_simple, value1)

    @given(value1=hst.integers())
    def test_combo_positional(self, value1: int) -> None:
        combo1 = onedigit.Combo(value1)
        self.check_combo(combo1, value1)

    # For serialization
    @given(value=hst.integers(min_value=1), cost=hst.integers(min_value=1))
    def test_combo_to_dictionary(self, value: int, cost: int) -> None:
        # Create a simple combo, and get its dictionary
        combo1 = onedigit.Combo(value=value, cost=cost, expr_full=str(value), expr_simple=str(value))
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
        combo1 = onedigit.Combo(value1)

        str1 = str(combo1)

        assert str1

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_ordering(self, value1: int, value2: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

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
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

        combo3 = combo1.binary_operation(combo2, "+")
        combo4 = combo2.binary_operation(combo1, "+")

        self.check_combo(combo3, value1 + value2)
        self.check_combo(combo4, value2 + value1)

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_subtraction(self, value1: int, value2: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

        combo3 = combo1.binary_operation(combo2, "-")
        combo4 = combo2.binary_operation(combo1, "-")

        self.check_combo(combo3, value1 - value2)
        self.check_combo(combo4, value2 - value1)

    @given(value1=hst.integers(), value2=hst.integers())
    def test_combo_multiplication(self, value1: int, value2: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

        combo3 = combo1.binary_operation(combo2, "*")
        combo4 = combo2.binary_operation(combo1, "*")

        self.check_combo(combo3, value1 * value2)
        self.check_combo(combo4, value2 * value1)

    @given(value1=hst.integers())
    def test_combo_integer_division_by_zero(self, value1: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(0)

        with self.assertRaises(expected_exception=ZeroDivisionError):
            combo3 = combo1.binary_operation(combo2, "/")
            assert combo3.value == 0

    @given(value1=hst.integers(min_value=1))
    def test_combo_integer_division_by_one(self, value1: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value1)

        combo3 = combo1.binary_operation(combo1, "/")
        combo4 = combo1.binary_operation(combo2, "/")

        self.check_combo(combo3, 1)
        self.check_combo(combo4, 1)

    @given(value1=hst.integers(min_value=1), value2=hst.integers(min_value=1))
    def test_combo_integer_division(self, value1: int, value2: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

        combo3 = combo1.binary_operation(combo2, "/")
        combo4 = combo2.binary_operation(combo1, "/")

        if (value1 % value2) == 0:
            self.check_combo(combo3, value1 // value2)
        else:
            self.check_combo(combo3, 0)

        if value2 % value1 == 0:
            self.check_combo(combo4, value2 // value1)
        else:
            self.check_combo(combo4, 0)

    @given(value1=hst.integers(min_value=1), value2=hst.integers(max_value=50))
    def test_combo_integer_exponentiation(self, value1: int, value2: int) -> None:
        combo1 = onedigit.Combo(value1)
        combo2 = onedigit.Combo(value2)

        combo3 = combo1.binary_operation(combo2, "^")

        # The object method protects against gigantic values.
        # But we also need to protect the tester from crashing
        # while evaluating that factorial.
        if (value1 < 0) or (value2 > 40):
            self.check_combo(combo3, 0)
            return

        self.check_combo(combo3, (value1**value2))

    @given(value1=hst.integers())
    def test_combo_sqrt(self, value1: int) -> None:
        combo1 = onedigit.Combo(value1)

        combo2 = combo1.unary_operation("sqrt")

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
        combo1 = onedigit.Combo(value1)

        combo2 = combo1.unary_operation("!")

        # The object method protects against gigantic values.
        # But we also need to protect the tester from crashing
        # while evaluating that factorial.
        if (value1 < 0) or (value1 > 20):
            self.check_combo(combo2, 0)
            return

        # FIXME, we cannot validate this expression yet
        # self.check_combo(combo2, expected1)
        assert combo2.value == math.factorial(value1)
