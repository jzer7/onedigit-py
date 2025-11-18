"""Make the CLI runnable using python -m onedigit."""

import sys

from .cli2 import cmdline2

sys.exit(0 if cmdline2() else 1)
