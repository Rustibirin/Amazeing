#!/usr/bin/env python3

"""
This script receives a configuration file, validates it,
and prepares the environment for maze generation.
"""

from enum import Enum
import sys
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
        parts = [p.strip() for p in val.split(",")]
        if len(parts) == 2 and all(p.isdigit() or (p.startswith('-')
           and p[1:].isdigit()) for p in parts):
            return (int(parts[0]), int(parts[1]))
        raise ValueError(f"Invalid tuple format: {val}")

    if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
        return int(val)

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
            config['SEED'] = 42
        if ('DELAY' not in config):
            config['DELAY'] = 0.03
    except FileNotFoundError:
        print(f"Error: File '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to read '{path}'.", file=sys.stderr)
        sys.exit(1)

    return config
