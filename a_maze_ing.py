#!/usr/bin/env python3

import sys
from time import sleep
from typing import Any

import configuration
from generator import MazeGenerator
import visualizer


def run_pipeline(
    grid: MazeGenerator,
    settings: dict[str, Any],
    show_path: bool = True,
) -> str:
    """
    Executes the maze pipeline: generation,
    solving, exporting, and optional animation.
    """
    print("Building and solving maze...")
    live = None
    if settings.get("LIVE_MODE"):
        live = visualizer.render_live

    grid.generate(
        animation=live,
        delay=settings.get("DELAY", 0.0),
    )
    solution = grid.solve()
    grid.export()

    if settings.get("LIVE_MODE") and grid.maze and show_path:
        visualizer.animate_solution(
            grid.maze,
            solution,
            delay=settings.get("DELAY", 0.0),
        )

    return solution


def run_menu(
    grid: MazeGenerator,
    settings: dict[str, Any],
    solution: str,
) -> None:
    """Handles the interactive terminal menu loop."""
    show_path: bool = True

    while True:
        if grid.maze:
            current_path = solution if show_path else ""
            visualizer.render_ascii(grid.maze, current_path)
            if not grid.maze.has_42:
                print(
                    "Warning: Maze dimensions are too "
                    "small to embed the '42' pattern."
                )
            if grid.maze.easter_egg:
                print("You found the Easter Egg. Congratulations!!")
            print(f"Live Mode: {settings.get('LIVE_MODE', False)}")

        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide the shortest path")
        print("3. Rotate wall colours")
        print("4. Toggle Live Animation")
        print("5. Quit")

        try:
            choice = input("Choice? (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program...")
            break

        if choice == "1":
            print("Re-generating maze...")
            settings.pop("SEED", None)
            solution = run_pipeline(grid, settings, show_path)

        elif choice == "2":
            if settings.get("LIVE_MODE") and grid.maze and not show_path:
                visualizer.animate_solution(
                    grid.maze,
                    solution,
                    delay=settings.get("DELAY", 0.00),
                )
            show_path = not show_path

        elif choice == "3":
            visualizer.rotate_color()

        elif choice == "4":
            settings["LIVE_MODE"] = not settings.get("LIVE_MODE", False)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from 1 to 5.")
            sleep(1)


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
        print("\033[H\033[J", end="")
        print("Validating configuration...")
        settings = configuration.parse_config(config_path)

        configuration.validate_config(settings)

        print()
        print("Configuration loaded and validated successfully!")
        print(f"Dimensions: {settings['WIDTH']}x{settings['HEIGHT']}")
        print(f"Entry: {settings['ENTRY']} | Exit: {settings['EXIT']}")
        print(f"Perfect Mode: {settings['PERFECT']}")
        print(f"Output file: {settings['OUTPUT_FILE']}")
        if "SEED" in settings:
            print(f"Seed: {settings['SEED']}")

        print()
        input("\nPress Enter to continue...")

        grid = MazeGenerator(settings)
        solution = run_pipeline(grid, settings)
        run_menu(grid, settings, solution)

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
