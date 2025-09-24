"""A standardized logger for the application."""

import logging
import logging.handlers

# Root logger : used only by other libraries
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

# Main Logger
_main_logger = logging.getLogger("onedigit")


# -----------------------------------------------------------
# Configure logging:
#   * Root logger: used by other packages
#   * Main logger: used by this package; every module creates
#     a child logger out of it.
# Log content:
#   * The console will get messages INFO and higher, things
#     we want the user to see right away.
#   * The log file will get messages DEBUG and higher,
#     information for post execution analysis
# -----------------------------------------------------------


def init_logger() -> None:
    """Init logger."""
    _main_logger.handlers = []

    _main_logger.setLevel(logging.INFO)
    _main_logger.setLevel(logging.DEBUG)

    # create formatters
    consoleformatter = logging.Formatter("%(levelname)s - %(message)s")
    fileformatter = logging.Formatter(
        "%(asctime)s, %(name)s, %(levelname)s, %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # create console handler used for higher log levels
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(consoleformatter)
    _main_logger.addHandler(ch)

    # create file handler which logs more information (lower level
    # errors, as well as time information)
    fh = logging.handlers.RotatingFileHandler(
        filename="calculate.log", maxBytes=100000, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fileformatter)
    _main_logger.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module, derived from the main logging object."""
    if name.startswith("onedigit."):
        start = name.find(".")
        name = name[start + 1 :]
    clogger = _main_logger.getChild(name)

    return clogger


# -----------------------------------------------------------
init_logger()
