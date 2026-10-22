#!/usr/bin/env python3

import os
import select
import sys
from time import sleep
from typing import Any
from pydantic import ValidationError

from mazegen import GameMode, MazeGenerator, parse_config
from ui import game_mode, visualizer


def flush_input() -> None:
    """
    Discard any key saved in buffer.
    """

    try:
        while select.select([sys.stdin], [], [], 0.0)[0]:
            os.read(sys.stdin.fileno(), 1024)
    except (OSError, ValueError):
        pass


def error_generator(msg: str) -> None:
    """
    Show an error and finalise the execution.
    """

    print("\033c", end="")
    print(msg, file=sys.stderr)
    sys.exit(1)


def toggle_game_mode(settings: dict[str, Any]) -> None:
    """
    Cycles through the available GameModes in the settings.
    """

    modes = list(GameMode)
    current_mode = settings.get("GAME_MODE", GameMode.BONUS)
    next_index = (modes.index(current_mode) + 1) % len(modes)
    settings["GAME_MODE"] = modes[next_index]


def run_pipeline(
    grid: MazeGenerator,
    settings: dict[str, Any],
    show_path: bool = True
) -> str:
    """
    Executes the maze pipeline: generation,
    solving, exporting, and optional animation.
    """

    live = None
    if settings.get("LIVE_MODE"):
        live = visualizer.render_live
    try:
        grid.generate(
            animation=live,
            delay=settings.get("DELAY", 0.0),
        )
        solution = grid.solve()
        grid.export()

        print("\033c", end="")
        if settings.get("LIVE_MODE") and grid.maze and show_path:
            visualizer.animate_solution(
                grid.maze,
                solution,
                delay=settings.get("DELAY", 0.0),
            )
    except KeyboardInterrupt:
        print("\033c", end="")
        if grid.maze is not None:
            solution = grid.solve()
            grid.export()
            visualizer.render_ascii(grid.maze, solution)
        else:
            solution = ""

    return solution


def run_menu(
    grid: MazeGenerator,
    settings: dict[str, Any],
    solution: str,
    config_path: str
) -> None:
    """
    Handles the interactive terminal menu loop.
    """

    show_path: bool = False
    base_settings: dict[str, Any] = settings.copy()
    while True:
        if grid.maze:
            current_path = solution if show_path else ""
            print("\033c", end="")
            visualizer.render_ascii(grid.maze, current_path)
            print("\n=== Show Mode ===")
            if grid.maze.small_grid:
                print(
                    "Warning: Maze dimensions are too "
                    "small to stamp the '42' pattern."
                )
            else:
                if not grid.maze.has_42:
                    print(
                        "Warning: The ENTRY or EXIT overlaps with "
                        "the '42' pattern. Cannot stamp it"
                    )

            if grid.maze.easter_egg:
                print("You found the Easter Egg. Congratulations!!")
            print(f"Live Mode: {settings.get('LIVE_MODE', False)}")
            print(f"Perfect Mode: {settings['PERFECT']}")
            if not settings["PERFECT"]:
                print(
                    f"Game Mode: "
                    f"{settings.get('GAME_MODE', GameMode.BONUS).name}"
                )

        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide the shortest path")
        print("3. Rotate wall colours")
        print("4. Toggle Live Animation")
        print("5. Toggle Perfect Mode")
        print("6. Toggle Game Mode (Imperfect mode)")
        print("7. Charge new settings")
        print("8. PLAY MAZE!")
        print("9. Quit")
        print("\033[J")

        flush_input()

        try:
            choice = input("Choice? (1-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program...")
            break

        if choice == "1":
            print("Re-generating maze...")
            sleep(0.5)
            settings.pop("SEED", None)
            try:
                grid = MazeGenerator(settings=settings)
            except ValidationError as ex:
                error_generator(ex.errors()[0]["msg"])
            solution = run_pipeline(grid, settings, show_path)

        elif choice == "2":
            if settings.get("LIVE_MODE") and grid.maze and not show_path:
                try:
                    visualizer.animate_solution(
                        grid.maze,
                        solution,
                        delay=settings.get("DELAY", 0.00),
                    )
                except KeyboardInterrupt:
                    settings['LIVE_MODE'] = False
                    visualizer.render_ascii(grid.maze, solution)
            show_path = not show_path

        elif choice == "3":
            visualizer.rotate_color()

        elif choice == "4":
            settings["LIVE_MODE"] = not settings.get("LIVE_MODE", False)

        elif choice == "5":
            settings["PERFECT"] = not settings["PERFECT"]
            grid = MazeGenerator(settings=settings)
            solution = run_pipeline(grid, settings, show_path)

        elif choice == "6":
            if settings["PERFECT"]:
                continue
            toggle_game_mode(settings)
            grid = MazeGenerator(settings=settings)
            solution = run_pipeline(grid, settings, show_path)

        elif choice == "7":
            try:
                new_settings = load_settings(config_path)
                if new_settings == base_settings:
                    print("No changes detected in configuration file.")
                    sleep(0.5)
                    continue

                settings = new_settings
                base_settings = new_settings.copy()
                print("Re-generating maze with new configuration...")
                settings.pop("SEED", None)
                try:
                    grid = MazeGenerator(settings=settings)
                except ValidationError as ex:
                    error_generator(ex.errors()[0]["msg"])
                solution = run_pipeline(grid, settings, show_path)
            except Exception as e:
                print(f"Error loading settings: {e}")
                sleep(0.5)

        elif choice == "8":
            if grid.maze:
                game_mode.play_interactive(grid.maze)

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from 1 to 9.")
            sleep(0.5)


def load_settings(config_path: str) -> dict[str, Any]:
    """
    Charge the config parameters in a valid dictionary.
    """

    settings = parse_config(config_path)
    return settings


def main() -> None:
    """
    Program entry point.
    """

    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <configuration_file>",
            file=sys.stderr
        )
        sys.exit(1)

    config_path: str = sys.argv[1]

    print("\033c", end="")
    print("Validating configuration...")
    try:
        settings = load_settings(config_path)

        print()
        print("Configuration loaded and validated successfully!")
        print(f"Dimensions: {settings['WIDTH']}x{settings['HEIGHT']}")
        print(f"Entry: {settings['ENTRY']} | Exit: {settings['EXIT']}")
        print(f"Perfect Mode: {settings['PERFECT']}")
        print(f"Output file: {settings['OUTPUT_FILE']}")
        if "SEED" in settings:
            print(f"Seed: {settings['SEED']}")

        flush_input()
        input("\nPress Enter to continue...")
        print("\033c", end="")

        try:
            grid = MazeGenerator(settings=settings)
        except ValidationError as ex:
            error_generator(ex.errors()[0]["msg"])

        solution = run_pipeline(grid, settings)
        run_menu(grid, settings, solution, config_path)

    except FileNotFoundError:
        print(f"Error: File '{config_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nExiting the program.")

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
