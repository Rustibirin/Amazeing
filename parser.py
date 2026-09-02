#!/usr/bin/env python3

"""
This script receives a configuration file, validates it,
and prepares the environment for maze generation.
"""

from typing import Any, Dict, Tuple


def parse_config(file_path: str) -> Dict[str, Any]:
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
# Permitimos claves duplicadas??

    config_data: Dict[str, Any] = {}

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

            if key in ("WIDTH", "HEIGHT"):
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

            elif key == "PERFECT":
                if val.lower() not in ("true", "false"):
                    raise ValueError(
                        f"Invalid value for PERFECT on line {line_num}: "
                        f"expected 'True' or 'False'."
                    )
                config_data[key] = val.lower() == "true"

            elif key == "SEED":
                try:
                    config_data[key] = int(val)
                except ValueError:
                    raise ValueError(
                        f"Error on line {line_num}: "
                        f"Invalid value for SEED."
                    ) from None

# ---> Yo mostraría el SEED por pantalla y generaría uno aleatorio
# si el usuario no lo proporciona, pero tenemos que hablarlo.

            else:
                config_data[key] = val

    return config_data


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validates that the maze parameters are correct and logically consistent.

    Args:
        config: Dictionary containing the data extracted
        from the configuration file.

    Raises:
        ValueError: If any required key is missing or the values are invalid.
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
    entry: Tuple[int, int] = config["ENTRY"]
    exit_node: Tuple[int, int] = config["EXIT"]

    if width <= 3 or height <= 3:
        raise ValueError(
            "WIDTH and HEIGHT must be greater than tree."
        )

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError(
            f"Entry {entry} is outside the maze boundaries."
        )

    if not (0 <= exit_node[0] < width and 0 <= exit_node[1] < height):
        raise ValueError(
            f"Exit {exit_node} is outside the maze boundaries."
        )

    if entry == exit_node:
        raise ValueError(
            "Entry and exit cannot be in the same cell."
        )
