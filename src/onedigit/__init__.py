"""Evaluate expressions that use a single digit from 1 to 9, and basic arithmetic operations."""

from onedigit.cli import main
from onedigit.cli2 import cmdline2
from onedigit.model import Combo, Model
from onedigit.simple import advance, calculate, get_model

__uri__ = "https://github.com/jzer7/onedigit-py"
__version__ = "0.2.0"


__all__ = [
    "Combo",
    "Model",
    "advance",
    "calculate",
    "cmdline2",
    "get_model",
    "main",
]
