import unittest

import onedigit


class TestCalculate(unittest.TestCase):
    def test_main_entry(self) -> None:
        assert onedigit.app_old(1, max_value=1, max_cost=1)
