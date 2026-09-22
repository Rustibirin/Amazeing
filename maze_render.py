import sys
from typing import Any


def print_sqr(color1: str) -> None:
    print(color1*2, end="")
    sys.stdout.flush()


def print_border(width: int, color: str) -> None:
    for _ in range(width*2 + 1):
        print_sqr(color)
    print()


def print_maze(settings: dict[str, Any], maze: list[list[int]],
               width: int, height: int, colors: list[str],
               sol: list[tuple[int, int]] = []) -> None:
    print_border(width, colors[0])
    entry_coords = settings['ENTRY']
    exit_coords = settings['EXIT']
    for row in range(height):
        print_sqr(colors[0])
        for col in range(width):
            if (maze[row][col] == 15):
                print_sqr(colors[4])
            elif (entry_coords == (col, row) or exit_coords == (col, row)):
                print_sqr(colors[2])
            elif (sol and (row, col) in sol):
                print_sqr(colors[3])
            else:
                print_sqr(colors[1])
            if (maze[row][col] % 4 >= 2):
                print_sqr(colors[0])
            else:
                if (sol and (row, col) in sol and (row, col + 1) in sol):
                    print_sqr(colors[3])
                else:
                    print_sqr(colors[1])
        print()
        print_sqr(colors[0])
        for col in range(width):
            if (maze[row][col] % 8 >= 4):
                print_sqr(colors[0])
            else:
                if (sol and (row, col) in sol and (row + 1, col) in sol):
                    print_sqr(colors[3])
                else:
                    print_sqr(colors[1])
            print_sqr(colors[0])
        print()


def read_fich(name: str) -> list[list[int]]:
    HEX_DICT: dict[str, int] = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
            '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13,
            'e': 14, 'f': 15
        }
    maze = []
    rows = []
    fich = open(name, "r")
    text = fich.read()
    for row in text.split("\n"):
        for letter in row:
            rows.append(HEX_DICT[letter])
        maze.append(rows)
        rows = []
    return (maze)


def gen_palette() -> list[list[str]]:
    palette = []

    colors = []
    colors.append("\033[38;5;16m\033[48;5;16m \033[0m")
    colors.append("\033[38;5;254m\033[48;5;254m \033[0m")
    colors.append("\033[38;5;134m\033[48;5;134m \033[0m")
    colors.append("\033[38;5;207m\033[48;5;207m \033[0m")
    colors.append("\033[38;5;220m\033[48;5;220m \033[0m")

    palette.append(colors)

    colors = []
    colors.append("\033[38;5;38m\033[48;5;38m \033[0m")
    colors.append("\033[38;5;230m\033[48;5;230m \033[0m")
    colors.append("\033[38;5;94m\033[48;5;94m \033[0m")
    colors.append("\033[38;5;173m\033[48;5;173m \033[0m")
    colors.append("\033[38;5;236m\033[48;5;236m \033[0m")
    palette.append(colors)

    colors = []
    colors.append("\033[38;5;204m\033[48;5;204m \033[0m")
    colors.append("\033[38;5;194m\033[48;5;194m \033[0m")
    colors.append("\033[38;5;23m\033[48;5;23m \033[0m")
    colors.append("\033[38;5;70m\033[48;5;70m \033[0m")
    colors.append("\033[38;5;42m\033[48;5;42m \033[0m")
    palette.append(colors)

    colors = []
    colors.append("\033[38;5;160m\033[48;5;160m \033[0m")
    colors.append("\033[38;5;219m\033[48;5;219m \033[0m")
    colors.append("\033[38;5;41m\033[48;5;41m \033[0m")
    colors.append("\033[38;5;118m\033[48;5;118m \033[0m")
    colors.append("\033[38;5;44m\033[48;5;44m \033[0m")
    palette.append(colors)

    colors = []
    colors.append("\033[38;5;128m\033[48;5;128m \033[0m")
    colors.append("\033[38;5;123m\033[48;5;123m \033[0m")
    colors.append("\033[38;5;235m\033[48;5;235m \033[0m")
    colors.append("\033[38;5;246m\033[48;5;246m \033[0m")
    colors.append("\033[38;5;124m\033[48;5;226m \033[0m")
    palette.append(colors)

    return (palette)


def render(settings: dict[str, Any], cont_colors: int,
           solution: list[tuple[int, int]] = []) -> None:
    print("\033[2J\033[3J\033[H", end="", flush=True)
    width: int = settings['WIDTH']
    height: int = settings['HEIGHT']
    palette: list[list[str]] = gen_palette()

    color_choice: list[str] = palette[cont_colors % len(palette)]
    maze = read_fich(settings['OUTPUT_FILE'])
    if (solution):
        print_maze(settings, maze, width, height, color_choice, solution)
    else:
        print_maze(settings, maze, width, height, color_choice)
    print()
