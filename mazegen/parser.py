"""
This script receives a configuration file, validates it,
and prepares the environment for maze generation.
"""

import sys
from enum import Enum

from typing import Any


class Difficulty(float, Enum):
    """
    Maze difficulty levels mapped to dead-end removal rates.
    """

    BONUS = 1.0
    EASY = 0.8
    MEDIUM = 0.5
    HARD = 0.3
    INSANE = 0.1


def parse_val(val: str) -> Any:
    """
    Parse basic types and tuples of points.
    """

    if val == "TRUE":
        return True
    if val == "FALSE":
        return False

    if "," in val:
        parts = val.split(",")

        if len(parts) == 2:
            try:
                x = int(parts[0])
                y = int(parts[1])
                return (x, y)
            except ValueError:
                pass

        raise ValueError(f"Invalid tuple format: {val}")

    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    return val


def parse_config(path: str) -> dict[str, Any]:
    """
    Extract all of the keys from the config_file
    and define them as the specific type.
    """

    config = {}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for num_line, line in enumerate(f, start=1):
                clean_line = line.split('#')[0].strip()
                if not clean_line:
                    continue

                if '=' not in clean_line:
                    text = f"Syntax error in the line {num_line}:"
                    print(f"{text} is missed '='", file=sys.stderr)
                    sys.exit(1)

                key, value = clean_line.split('=', 1)
                key, value = key.strip(), value.strip()
                if isinstance(value, str) and key in (
                    "PERFECT", "DIFFICULTY", "ALGORITHM"
                ):
                    value = value.upper()
                if key in config:
                    print("\033c", end="", flush=True)
                    print(f"Error: Duplicate key '{key}' in the file"
                          f" {path} found at line"
                          f" {num_line}", file=sys.stderr)
                    sys.exit(1)
                try:
                    config[key] = parse_val(value)
                except ValueError as e:
                    text = f"Error in line {num_line} to '{key}'"
                    print(f"{text}: {e}", file=sys.stderr)
                    sys.exit(1)
        if ('SEED' not in config):
            config['SEED'] = None
        if ('DELAY' not in config):
            config['DELAY'] = 0.03
        if ('ALGORITHM' not in config):
            config['ALGORITHM'] = "WILSON"
        if ('DIFFICULTY' not in config):
            config['DIFFICULTY'] = Difficulty.BONUS
    except FileNotFoundError:
        print(f"Error: File '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to read '{path}'.", file=sys.stderr)
        sys.exit(1)

    return config
