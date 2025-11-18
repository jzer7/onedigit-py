"""Make the CLI runnable using python -m onedigit."""

import sys

from .cli import app

sys.exit(0 if app() else 1)
