#!/usr/bin/env python3

import sys
from time import sleep
from typing import Any

import configuration
from generator import MazeGenerator
import visualizer
from configuration import GameMode
import game_mode


def toggle_game_mode(settings: dict[str, Any]) -> None:
    """Cycles through the available GameModes in the settings."""
    modes = list(GameMode)
    current_mode = settings.get("GAME_MODE", GameMode.BONUS)
    next_index = (modes.index(current_mode) + 1) % len(modes)
    settings["GAME_MODE"] = modes[next_index]


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
    try:
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
    except KeyboardInterrupt:
        solution = grid.solve()
        grid.export()
        visualizer.render_ascii(grid.maze, solution)

    return solution


def run_menu(
    grid: MazeGenerator,
    settings: dict[str, Any],
    solution: str,
    config_path: str
) -> None:
    """Handles the interactive terminal menu loop."""
    show_path: bool = False
    base_settings: dict = settings.copy()
    while True:
        if grid.maze:
            current_path = solution if show_path else ""
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
        print("6. Toggle Game Mode")
        print("7. Charge new settings")
        print("8. PLAY MAZE!")
        print("9. Quit")

        try:
            choice = input("Choice? (1-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program...")
            break

        if choice == "1":
            print("Re-generating maze...")
            settings.pop("SEED", None)
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

        elif choice == "6":
            toggle_game_mode(settings)
        
        elif choice == "7":
            try:
                new_settings = load_settings(config_path)
                if (new_settings == base_settings):
                    raise FileNotFoundError
                print("\033[0H\033[0J")
                settings = new_settings
                print("Re-generating maze...")
                settings.pop("SEED", None)
                grid = MazeGenerator(settings)
                solution = run_pipeline(grid, settings, show_path)
            except Exception:
                print("No more changes to reflect")
                sleep(1)

        elif choice == "8":
            if grid.maze:
                game_mode.play_interactive(grid.maze)

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from 1 to 9.")
            sleep(1)


def load_settings(config_path: str) -> dict[str, Any]:
    settings = configuration.parse_config(config_path)
    configuration.validate_config(settings)
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

        print()
        input("\nPress Enter to continue...")

        grid = MazeGenerator(settings)
        solution = run_pipeline(grid, settings)
        run_menu(grid, settings, solution, config_path)

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
    except KeyboardInterrupt:
        print("\nExiting the program.")

    except Exception as e:
        print(
            f"Unexpected error: {e}",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
