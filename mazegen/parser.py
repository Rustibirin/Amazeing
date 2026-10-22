#!/usr/bin/env python3

"""
Configuration parser and validator module for A-Maze-ing.
"""

from enum import Enum
import re
from typing import Any


class GameMode(float, Enum):
    """
    Maze difficulty levels mapped to dead-end removal rates.
    """

    BONUS = 1.0
    EASY = 0.8
    MEDIUM = 0.5
    HARD = 0.3
    INSANE = 0.1


def parse_config(file_path: str) -> dict[str, Any]:
    """
    Reads and processes the configuration file in KEY=VALUE format.
    Empty lines and comments starting with # are ignored.

    Args:
        file_path: Path to the configuration file.

    Returns:
        A dictionary containing the processed keys and values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If there is a syntax error in the file.
    """
    config_data: dict[str, Any] = {}
    pattern = re.compile(r"^[a-zA-Z0-9._-]+$")

    with open(file_path, mode="r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Syntax error on line {line_num}: Expected 'KEY=VALUE'."
                )
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()

            if key in config_data:
                raise ValueError(
                    f"Error on line {line_num}: Duplicate key found '{key}'."
                )

            if key in ("WIDTH", "HEIGHT", "SEED"):
                try:
                    config_data[key] = int(val)
                except ValueError:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid value for {key}."
                    ) from None

            elif key in ("ENTRY", "EXIT"):
                coords = val.split(",")
                if len(coords) != 2:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid coordinates for {key}."
                    )
                try:
                    x = int(coords[0].strip())
                    y = int(coords[1].strip())
                except ValueError:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid coordinates for {key}."
                    ) from None
                config_data[key] = (x, y)

            elif key == "OUTPUT_FILE":
                if (
                    not val
                    or len(val.encode("utf-8")) > 255
                    or not pattern.match(val)
                ):
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid character(s) or length for {key} '{val}'."
                    )
                config_data[key] = val

            elif key in ("PERFECT", "LIVE_MODE"):
                if val.lower() not in ("true", "false"):
                    raise ValueError(
                        f"Invalid value for {key} on line {line_num}: "
                        f"expected 'True' or 'False'."
                    )
                config_data[key] = val.lower() == "true"

            elif key == "GAME_MODE":
                if val.upper() not in GameMode.__members__:
                    raise ValueError(
                        f"Invalid value for GAME_MODE on line {line_num}: "
                        f"expected 'Easy', 'Medium', 'Hard' or 'Insane'."
                    )
                config_data[key] = GameMode[val.upper()]

            elif key == "DELAY":
                try:
                    config_data[key] = float(val)
                except ValueError:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid value for {key}."
                    ) from None

                if config_data[key] < 0:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"{key} cannot be negative."
                    )

            else:
                config_data[key] = val

    return config_data


def validate_config(config: dict[str, Any]) -> None:
    """
    Validates that the maze parameters are correct and logically consistent.

    Args:
        config: dictionary containing data extracted from config file.

    Raises:
        ValueError: If any required key is missing or values are invalid.
    """
    required_keys = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]

    for key in required_keys:
        if key not in config:
            raise ValueError(
                f"Required configuration key is missing: {key}"
            )

    width: int = config["WIDTH"]
    height: int = config["HEIGHT"]
    entry_point: tuple[int, int] = config["ENTRY"]
    exit_point: tuple[int, int] = config["EXIT"]

    if width <= 3 or height <= 3:
        raise ValueError(
            "WIDTH and HEIGHT must be greater than 3."
        )

    if not (0 <= entry_point[0] < width and 0 <= entry_point[1] < height):
        raise ValueError(
            f"Entry {entry_point} is outside the maze boundaries."
        )

    if not (0 <= exit_point[0] < width and 0 <= exit_point[1] < height):
        raise ValueError(
            f"Exit {exit_point} is outside the maze boundaries."
        )

    if entry_point == exit_point:
        raise ValueError(
            "Entry and exit cannot be in the same cell."
        )
