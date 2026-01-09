"""Evaluate expressions that use a single digit from 1 to 9, and basic arithmetic operations."""

from onedigit.cli import app
from onedigit.combo import Combo
from onedigit.model import Model
from onedigit.operations import binary_operation, unary_operation
from onedigit.simple import advance, calculate, get_model

__uri__ = "https://github.com/jzer7/onedigit-py"
__version__ = "0.3.0"


__all__ = [
    "__version__",
    "Combo",
    "Model",
    "advance",
    "app",
    "binary_operation",
    "calculate",
    "get_model",
    "unary_operation",
]
