import time
from typing import Any

# ANSI terminal colors
WALL_COLOR: str = "\033[1;33m█\033[0m"
PATH_COLOR: str = "\033[1;92m█\033[0m"
TEMPLATE_COLOR: str = "\033[32m█\033[0m"
ENTRY_COLOR: str = "\033[92mS\033[0m"
EXIT_COLOR: str = "\033[91mE\033[0m"
SPACE: str = " "

COLOR_PALETTES = [
    ("\033[1;33m█\033[0m", "\033[1;92m█\033[0m"),
    ("\033[1;34m█\033[0m", "\033[1;31m█\033[0m"),
    ("\033[1;35m█\033[0m", "\033[1;36m█\033[0m"),
    ("\033[38;5;208m█\033[0m", "\033[38;5;39m█\033[0m"),
]
current_palette_idx = 0


def rotate_color() -> None:
    """Rotates the global wall and path colors to the next palette."""
    global WALL_COLOR, PATH_COLOR, current_palette_idx
    current_palette_idx = (current_palette_idx + 1) % len(COLOR_PALETTES)
    WALL_COLOR, PATH_COLOR = COLOR_PALETTES[current_palette_idx]


def _stamp_start_and_exit(grid: list[list[str]], maze: Any) -> None:
    """Stamps the ENTRY ('S') and EXIT ('E') markers on top of the grid."""
    grid[maze.entry[1] * 2 + 1][maze.entry[0] * 2 + 1] = ENTRY_COLOR
    grid[maze.exit[1] * 2 + 1][maze.exit[0] * 2 + 1] = EXIT_COLOR


def _build_base_grid(maze: Any) -> list[list[str]]:
    """
    Constructs the base character grid
    with walls, passages, and templates.
    """
    grid_h = maze.height * 2 + 1
    grid_w = maze.width * 2 + 1
    grid = [[WALL_COLOR for _ in range(grid_w)] for _ in range(grid_h)]

    for y in range(maze.height):
        for x in range(maze.width):
            grid_y, grid_x = y * 2 + 1, x * 2 + 1

            if maze.is_solid(x, y):
                grid[grid_y][grid_x] = TEMPLATE_COLOR
                for move_x, move_y, _, _ in maze.DIR_MAP.values():
                    nx, ny = x + move_x, y + move_y
                    if maze.in_grid(nx, ny) and maze.is_solid(nx, ny):
                        grid[grid_y + move_y][grid_x + move_x] = TEMPLATE_COLOR
                continue

            if maze.in_maze(x, y):
                grid[grid_y][grid_x] = SPACE
                val = maze.matrix[y][x]
                for move_x, move_y, bit, _ in maze.DIR_MAP.values():
                    if not (val & bit):
                        grid[grid_y + move_y][grid_x + move_x] = SPACE

    _stamp_start_and_exit(grid, maze)
    return grid


def _draw_grid(grid: list[list[str]]) -> None:
    """Clears screen and prints the character canvas to the terminal."""
    print("\033[H\033[J", end="")
    for row in grid:
        print("".join(row))


def render_live(maze: Any, delay: float) -> None:
    """Renders only the current state of maze generation in real-time."""
    grid = _build_base_grid(maze)
    _draw_grid(grid)
    if delay > 0:
        time.sleep(delay)


def animate_solution(maze: Any, solution: str, delay: float) -> None:
    """Animates the solution path step-by-step on top of the rendered maze."""
    grid = _build_base_grid(maze)
    current_x, current_y = maze.entry

    for step in solution:
        grid_y, grid_x = current_y * 2 + 1, current_x * 2 + 1

        if (current_x, current_y) != maze.entry:
            grid[grid_y][grid_x] = PATH_COLOR

        move_x, move_y, _, _ = maze.DIR_MAP[step]
        grid[grid_y + move_y][grid_x + move_x] = PATH_COLOR

        current_x += move_x
        current_y += move_y

        _draw_grid(grid)
        if delay > 0:
            time.sleep(delay)

    _stamp_start_and_exit(grid, maze)
    _draw_grid(grid)


def render_ascii(maze: Any, solution: str = "") -> None:
    """
    Renders the complete maze at once,
    optionally overlaying the solution path.
    """
    grid = _build_base_grid(maze)

    if solution:
        current_x, current_y = maze.entry
        for step in solution:
            grid_y, grid_x = current_y * 2 + 1, current_x * 2 + 1
            grid[grid_y][grid_x] = PATH_COLOR

            move_x, move_y, _, _ = maze.DIR_MAP[step]
            grid[grid_y + move_y][grid_x + move_x] = PATH_COLOR

            current_x += move_x
            current_y += move_y

        grid[current_y * 2 + 1][current_x * 2 + 1] = PATH_COLOR

        _stamp_start_and_exit(grid, maze)

    _draw_grid(grid)
