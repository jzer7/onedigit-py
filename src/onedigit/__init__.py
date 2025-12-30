"""Evaluate expressions that use a single digit from 1 to 9, and basic arithmetic operations."""

from onedigit.cli import app
from onedigit.model import Combo, Model
from onedigit.simple import advance, calculate, get_model

__uri__ = "https://github.com/jzer7/onedigit-py"
__version__ = "0.3.0"


__all__ = [
    "__version__",
    "Combo",
    "Model",
    "advance",
    "app",
    "calculate",
    "get_model",
]
