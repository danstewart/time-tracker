"""
The core logger creator
To change log level system wide set LEVEL_OVERRIDE

To enable logging in just one package then edit the get_logger call for that package
"""

import os
import logging

LEVEL_OVERRIDE_APPLIES_TO = ()
LEVEL_OVERRIDE = None

# Allow setting level via the LOG_LEVEL env var
# Format is ${LEVEL}:${LOG_NAME_1},${LOG_NAME_2},${LOG_NAME_N}
# LOG_NAME is an optional comma separate list of log handler names
# If not specified then the level will apply to all handlers
if level_override := os.getenv("LOG_LEVEL"):
    applies_to = ()
    if ":" in level_override:
        level_override, applies_to = level_override.split(":")
        applies_to = applies_to.split(",")

    if hasattr(logging, level_override.upper()):
        LEVEL_OVERRIDE = getattr(logging, level_override.upper())
        LEVEL_OVERRIDE_APPLIES_TO = tuple(applies_to)


def get_logger(name="log-my-time-log", level=logging.WARNING, force_init=False):
    logger = logging.getLogger(name)

    if LEVEL_OVERRIDE and (not LEVEL_OVERRIDE_APPLIES_TO or name in LEVEL_OVERRIDE_APPLIES_TO):
        level = LEVEL_OVERRIDE

    # If logger has already been initialised then use it as is
    # Change the level here so if we change the level on an already ininitialised logger
    # it will work and you don't need to go searching for the first call
    if not force_init and logger.hasHandlers():
        logger.setLevel(level)
        return logger

    formatter = logging.Formatter("[%(asctime)s | %(name)s] %(levelname)s in %(module)s: %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
