#!/usr/bin/env python3

"""
This script receives a configuration file, validates it,
and prepares the environment for maze generation.
"""

import re
from typing import Any
from enum import Enum
import sys


class GameMode(float, Enum):
    """Maze difficulty levels mapped to dead-end removal rates."""

    BONUS = 1.0
    EASY = 0.8
    MEDIUM = 0.5
    HARD = 0.3
    INSANE = 0.1


def parse_val(val: str) -> dict:
    """Parsea tipos primitivos y tuplas especificas."""
    if val in ("True", "true"):
        return True
    if val in ("False", "false"):
        return False

    if "," in val:
        partes = [p.strip() for p in val.split(",")]
        if len(partes) == 2 and all(p.isdigit() or (p.startswith('-') and p[1:].isdigit()) for p in partes):
            return (int(partes[0]), int(partes[1]))
        raise ValueError(f"Invalid tuple format: {val}")

    if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
        return int(val)

    try:
        return float(val)
    except ValueError:
        pass

    return val


def parse_config(path: str) -> dict:
    config = {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for num_line, line in enumerate(f, start=1):
                clean_line = line.split('#')[0].strip()
                if not clean_line:
                    continue

                if '=' not in clean_line:
                    print(f"Syntax error in the line {num_line}: is missed '='", file=sys.stderr)
                    sys.exit(0)

                key, value = clean_line.split('=', 1)
                key, value = key.strip(), value.strip()

                try:
                    config[key] = parse_val(value)
                except ValueError as e:
                    print(f"Error in line {num_line} to '{key}': {e}", file=sys.stderr)
                    sys.exit(0)

    except FileNotFoundError:
        print(f"Error: '{path}' no existe.", file=sys.stderr)
        sys.exit(0)
    except PermissionError:
        print(f"Error: No allow to read '{path}'.", file=sys.stderr)
        sys.exit(0)

    return config
