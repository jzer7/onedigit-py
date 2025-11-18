import unittest

import onedigit


class TestCalculate(unittest.TestCase):
    def test_main_entry(self) -> None:
        assert onedigit.main(1, max_value=1, max_cost=1)
