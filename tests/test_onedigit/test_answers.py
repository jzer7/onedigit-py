import unittest

from hypothesis import given
from hypothesis import strategies as hst

import onedigit


class TestAnswers(unittest.TestCase):
    @given(
        digit=hst.integers(min_value=1, max_value=9),
        max_value=hst.integers(min_value=10, max_value=50),
        max_cost=hst.integers(min_value=1, max_value=10),
        max_steps=hst.integers(min_value=2, max_value=3),
    )
    def test_answers(self, digit: int, max_value: int, max_cost: int, max_steps: int) -> None:
        model = onedigit.Model(digit=digit)
        assert model is not None
        model.seed(max_value=max_value, max_cost=max_cost)
        onedigit.advance(mymodel=model, max_steps=max_steps)

        for combo in model.get_valid_combos():
            val, cost = combo.value, combo.cost
            expr_full, expr_simple = combo.expr_full, combo.expr_simple

            # Check cost is correct
            assert cost == expr_full.count(str(digit))

            # Ensure upper value was respected
            assert val <= max_value

            assert expr_simple

            assert expr_full
