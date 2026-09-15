#!/usr/bin/env python3

import sys
import configuration
from maze_generator import MazeGenerator
from maze_render import render
import random
from typing import Any


class Menu():
    def __init__(self, settings: dict[str, str | int]):
        self.settings: dict[str, str | int] = settings
        self.colors: int = 0
        self.show_solution: bool = False

    def play(self, flag: int,
             sol: list[tuple[int, int]] = []
             ) -> tuple[str, list[tuple[int, int]]]:
        if (flag == 1):
            maze = MazeGenerator(self.settings)
            sol = maze.generation()
        if (self.show_solution):
            render(self.settings, self.colors, sol)
        else:
            render(self.settings, self.colors, [])
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Change the wall colours")
        print("4. Reload settings")
        print("5. Quit")

        return (input("Choice? (1-5): ").strip(), sol)


def read_config(config_path: str) -> dict[str, str | int]:
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

    else:
        return (settings)


def main() -> None:
    """Program entry point."""

    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <configuration_file>",
            file=sys.stderr
        )
        sys.exit(1)

    config_path: str = sys.argv[1]
    settings: dict[str, Any] = read_config(config_path)
    random.seed(settings['SEED'])

    main_menu = Menu(settings)
    choice, solution = main_menu.play(1)
    while (choice != "5"):
        if (choice == "1"):
            choice, solution = main_menu.play(1, solution)
        elif (choice == "2"):
            main_menu.show_solution = not main_menu.show_solution
            choice, solution = main_menu.play(0, solution)
        elif (choice == "3"):
            main_menu.colors += 1
            choice, solution = main_menu.play(0, solution)
        elif (choice == "4"):
            settings = read_config(config_path)
            if (settings != main_menu.settings):
                main_menu.settings = settings
                choice, solution = main_menu.play(1, solution)
            else:
                choice, solution = main_menu.play(0, solution)
        else:
            choice, solution = main_menu.play(0, solution)


if __name__ == "__main__":
    main()
