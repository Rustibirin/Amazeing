#!/usr/bin/env python3

import sys
from parser import parse_config, validate_config


def main() -> None:
    """Program entry point."""

    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <configuration_file>",
            file=sys.stderr
        )
        sys.exit(1)

    config_path: str = sys.argv[1]

    try:
        config = parse_config(config_path)

        validate_config(config)

        print("Configuration loaded and validated successfully!")
        print(f"Dimensions: {config['WIDTH']}x{config['HEIGHT']}")
        print(f"Entry: {config['ENTRY']} | Exit: {config['EXIT']}")
        print(f"Perfect Mode: {config['PERFECT']}")
        print(f"Output file: {config['OUTPUT_FILE']}")

    except FileNotFoundError:
        print(
            f"Error: The file '{config_path}' does not exist.",
            file=sys.stderr
        )
        sys.exit(1)

    except ValueError as err:
        print(
            f"Configuration error: {err}",
            file=sys.stderr
        )
        sys.exit(1)

    except Exception as err:
        print(
            f"An unexpected error occurred: {err}",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
