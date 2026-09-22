import time
from typing import Any

# ANSI terminal colors
WALL_COLOR: int = 0
PATH_COLOR: int = 1
ENT_EX_COLOR: int = 2
SOLUTION_COLOR: int = 3
TEMPLATES_COLOR: int = 4
PALETTE: tuple[str] = ("", "", "", "", "")

COLOR_PALETTES = [
    ("\033[38;5;16m\033[48;5;16m \033[0m",
     "\033[38;5;207m\033[48;5;207m \033[0m",
     "\033[38;5;134m\033[48;5;134m \033[0m",
     "\033[38;5;254m\033[48;5;254m \033[0m",
     "\033[38;5;220m\033[48;5;220m \033[0m"),
    ("\033[38;5;38m\033[48;5;38m \033[0m",
     "\033[38;5;173m\033[48;5;173m \033[0m",
     "\033[38;5;94m\033[48;5;94m \033[0m",
     "\033[38;5;230m\033[48;5;230m \033[0m",
     "\033[38;5;236m\033[48;5;236m \033[0m"),
    ("\033[38;5;204m\033[48;5;204m \033[0m",
     "\033[38;5;70m\033[48;5;70m \033[0m",
     "\033[38;5;23m\033[48;5;23m \033[0m",
     "\033[38;5;194m\033[48;5;194m \033[0m",
     "\033[38;5;42m\033[48;5;42m \033[0m"),
    ("\033[38;5;160m\033[48;5;160m \033[0m",
     "\033[38;5;118m\033[48;5;118m \033[0m",
     "\033[38;5;41m\033[48;5;41m \033[0m",
     "\033[38;5;219m\033[48;5;219m \033[0m",
     "\033[38;5;44m\033[48;5;44m \033[0m"),
    ("\033[38;5;128m\033[48;5;128m \033[0m",
     "\033[38;5;246m\033[48;5;246m \033[0m",
     "\033[38;5;235m\033[48;5;235m \033[0m",
     "\033[38;5;123m\033[48;5;123m \033[0m",
     "\033[38;5;124m\033[48;5;226m \033[0m"),
]
current_palette_idx = 0


def rotate_color() -> None:
    """Rotates the global wall and path colors to the next palette."""
    global PALETTE, current_palette_idx
    current_palette_idx = (current_palette_idx + 1) % len(COLOR_PALETTES)
    PALETTE = COLOR_PALETTES[current_palette_idx]


def _stamp_start_and_exit(grid: list[list[str]], maze: Any) -> None:
    """
    Stamps the ENTRY and EXIT with and specific color
    markers on top of the grid.
    """
    grid[maze.entry[1] * 2 + 1][maze.entry[0] * 2 + 1] = PALETTE[ENT_EX_COLOR]
    grid[maze.exit[1] * 2 + 1][maze.exit[0] * 2 + 1] = PALETTE[ENT_EX_COLOR]


def _build_base_grid(maze: Any) -> list[list[str]]:
    """
    Constructs the base character grid
    with walls, passages, and templates.
    """
    grid_h = maze.height * 2 + 1
    grid_w = maze.width * 2 + 1
    grid = [[PALETTE[WALL_COLOR] 
             for _ in range(grid_w)] for _ in range(grid_h)]

    for y in range(maze.height):
        for x in range(maze.width):
            grid_y, grid_x = y * 2 + 1, x * 2 + 1

            if maze.is_solid(x, y):
                grid[grid_y][grid_x] = PALETTE[TEMPLATE_COLOR]
                for move_x, move_y, _, _ in maze.DIR_MAP.values():
                    nx, ny = x + move_x, y + move_y
                    if maze.in_grid(nx, ny) and maze.is_solid(nx, ny):
                        grid[grid_y + move_y][grid_x + move_x] = PALETTE[TEMPLATE_COLOR]
                continue

            if maze.in_maze(x, y):
                grid[grid_y][grid_x] = PALETTE[SOLUTION_COLOR]
                val = maze.matrix[y][x]
                for move_x, move_y, bit, _ in maze.DIR_MAP.values():
                    if not (val & bit):
                        grid[grid_y + move_y][grid_x + move_x] = PALETTE[SOLUTION_COLOR]

    _stamp_start_and_exit(grid, maze)
    return grid


def _draw_grid(grid: list[list[str]]) -> None:
    """Clears screen and prints the character canvas to the terminal."""
    print("\033[H\033[J", end="")
    for row in grid:
        for elm in row:
            print(elm * 2, end="")
        print()


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
            grid[grid_y][grid_x] = PALETTE[PATH_COLOR]

        move_x, move_y, _, _ = maze.DIR_MAP[step]
        grid[grid_y + move_y][grid_x + move_x] = PALETTE[PATH_COLOR]

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
    global PALETTE

    PALETTE = COLOR_PALETTES[current_palette_idx]
    grid = _build_base_grid(maze)
    if solution:
        current_x, current_y = maze.entry
        for step in solution:
            grid_y, grid_x = current_y * 2 + 1, current_x * 2 + 1
            grid[grid_y][grid_x] = PALETTE[PATH_COLOR]
            move_x, move_y, _, _ = maze.DIR_MAP[step]
            grid[grid_y + move_y][grid_x + move_x] = PALETTE[PATH_COLOR]

            current_x += move_x
            current_y += move_y

        grid[current_y * 2 + 1][current_x * 2 + 1] = PALETTE[PATH_COLOR]

        _stamp_start_and_exit(grid, maze)

    _draw_grid(grid)
