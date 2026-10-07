"""Interactive WASD player navigation and game mode logic."""

import sys
import termios
import tty
import visualizer
import subprocess

from typing import Any


def _get_key() -> str:
    """
    Captures a single key press from the standard input
    without requiring the user to press Enter.
    """

    fd = sys.stdin.fileno()
    terminal_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, terminal_settings)

    return key.lower()


def _play_sound(file_path: str = "victory.wav") -> None:
    """
    Plays a sound file.
    """

    try:
        subprocess.run(["aplay", file_path], stderr=subprocess.DEVNULL)

    except FileNotFoundError:
        pass


def play_interactive(maze: Any) -> None:
    """
    Main loop for the interactive WASD movement mode.
    """

    current_x, current_y = maze.entry

    while True:
        visualizer.render_playable(maze, current_x, current_y)

        print("\n=== Play Mode ===")
        print("Move: [W] Up | [S] Down | [A] Left | [D] Right")
        print("Quit: [Q] Return to main menu")

        if (current_x, current_y) == maze.exit:
            _play_sound()
            print("CONGRATULATIONS! You escaped the maze!")
            input("Press Enter to continue...")
            break

        key = _get_key()

        if key == "q":
            break
        elif (
            key == "w"
            and not maze.has_wall(current_x, current_y, maze.NORTH)
        ):
            current_y -= 1
        elif (
            key == "s"
            and not maze.has_wall(current_x, current_y, maze.SOUTH)
        ):
            current_y += 1
        elif (
            key == "a"
            and not maze.has_wall(current_x, current_y, maze.WEST)
        ):
            current_x -= 1
        elif (
            key == "d"
            and not maze.has_wall(current_x, current_y, maze.EAST)
        ):
            current_x += 1
