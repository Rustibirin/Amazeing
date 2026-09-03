#!/usr/bin/env python3

import sys
import configuration


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
        settings = configuration.parse_config(config_path)

        configuration.validate_config(settings)

        print("Configuration loaded and validated successfully!")
        print(f"Dimensions: {settings['WIDTH']}x{settings['HEIGHT']}")
        print(f"Entry: {settings['ENTRY']} | Exit: {settings['EXIT']}")
        print(f"Perfect Mode: {settings['PERFECT']}")
        print(f"Output file: {settings['OUTPUT_FILE']}")

    except FileNotFoundError:
        print(
            f"Error: The file '{config_path}' does not exist.",
            file=sys.stderr
        )
        sys.exit(1)

    except ValueError as e:
        print(
            f"Configuration error: {e}",
            file=sys.stderr
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"Unexpected error: {e}",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
