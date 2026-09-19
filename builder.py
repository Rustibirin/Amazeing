"""Maze generation and pathfinding engine."""

import random
from typing import Any, Callable, Dict, Tuple


class Builder:
    """
    Handles maze generation logic using
    Wilson's algorithm and Pac-Man mode.
    """

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:
        if seed is None:
            seed = random.randint(1, 2**31 - 1)

        self.seed = seed
        random.seed(self.seed)

    def build(
        self,
        maze: Any,
        perfect: bool,
        delay: float,
        game_mode: float = 0.8,
        animation: Callable[[Any, float], None] | None = None,
    ) -> None:
        """Executes the maze generation pipeline."""
        self._create_perfect_maze(maze, animation, delay)

        if not perfect:
            self._pacman_mode(maze, delay, game_mode, animation)

    def _create_perfect_maze(
        self,
        maze: Any,
        animation: Callable[[Any, float], None] | None,
        delay: float,
    ) -> None:
        valid_grid: list[Tuple[int, int]] = [
            (x, y)
            for x in range(maze.width)
            for y in range(maze.height)
            if not maze.is_solid(x, y)
        ]

        if not valid_grid:
            return

        start_cell = random.choice(valid_grid)
        maze.mark_in_maze(start_cell[0], start_cell[1])
        cells_in_maze = 1
        total_valid = len(valid_grid)

        while cells_in_maze < total_valid:
            unvisited = []

            for x, y in valid_grid:
                if not maze.in_maze(x, y) and not maze.is_solid(x, y):
                    unvisited.append((x, y))

            if not unvisited:
                break

            walk_start = random.choice(unvisited)
            current = walk_start

            walk: Dict[Tuple[int, int], Tuple[Tuple[int, int], int, int]] = {}

            while not maze.in_maze(current[0], current[1]):
                current_x, current_y = current
                valid_neighbor = []

                for move_x, move_y, bit, opp_bit in maze.DIR_MAP.values():
                    next_x, next_y = current_x + move_x, current_y + move_y
                    if (
                        maze.in_grid(next_x, next_y)
                        and not maze.is_solid(next_x, next_y)
                    ):
                        valid_neighbor.append(((next_x, next_y), bit, opp_bit))

                next_cell, bit, opp_bit = random.choice(valid_neighbor)
                walk[current] = (next_cell, bit, opp_bit)
                current = next_cell

            cell_ptr = walk_start

            while not maze.in_maze(cell_ptr[0], cell_ptr[1]):
                maze.mark_in_maze(cell_ptr[0], cell_ptr[1])
                cells_in_maze += 1

                next_cell, bit, opp_bit = walk[cell_ptr]
                current_x, current_y = cell_ptr
                next_x, next_y = next_cell

                maze.break_wall(
                    current_x, current_y, bit, opp_bit, next_x, next_y
                )

                if animation:
                    animation(maze, delay)

                cell_ptr = next_cell

    def _pacman_mode(
        self,
        maze: Any,
        delay: float,
        game_mode: float,
        animation: Callable[[Any, float], None] | None,
    ) -> None:
        self._open_corners(maze, delay, animation)
        self._break_dead_ends(maze, game_mode, delay, animation)

    def _open_corners(
        self,
        maze: Any,
        delay: float,
        animation: Callable[[Any, float], None] | None,
    ) -> None:
        corners = [
            (0, 0, maze.EAST, maze.SOUTH),
            (maze.width - 1, 0, maze.WEST, maze.SOUTH),
            (0, maze.height - 1, maze.EAST, maze.NORTH),
            (maze.width - 1, maze.height - 1, maze.WEST, maze.NORTH),
        ]

        for x, y, dir1, dir2 in corners:
            if not maze.is_solid(x, y):
                for move_x, move_y, bit, opp_bit in maze.DIR_MAP.values():
                    if bit in (dir1, dir2):
                        next_x, next_y = x + move_x, y + move_y
                        if (
                            maze.in_grid(next_x, next_y)
                            and not maze.is_solid(next_x, next_y)
                        ):
                            maze.break_wall(x, y, bit, opp_bit, next_x, next_y)

                            if animation:
                                animation(maze, delay)

    def _break_dead_ends(
        self,
        maze: Any,
        game_mode: float,
        delay: float,
        animation: Callable[[Any, float], None] | None,
    ) -> None:
        """breaks dead ends by tearing down extra walls, creating loops."""
        dead_ends: list[Tuple[int, int]] = []

        for y in range(maze.height):
            for x in range(maze.width):
                if maze.is_solid(x, y):
                    continue

                walls_count = 0
                for bit in (maze.NORTH, maze.EAST, maze.SOUTH, maze.WEST):
                    if maze.has_wall(x, y, bit):
                        walls_count += 1

                if walls_count == 3:
                    dead_ends.append((x, y))

        random.shuffle(dead_ends)
        ends_to_break = int(len(dead_ends) * game_mode)
        targets = dead_ends[0:ends_to_break]

        for current_x, current_y in targets:
            closed_neighbors = []
            for move_x, move_y, bit, opp_bit in maze.DIR_MAP.values():
                next_x, next_y = current_x + move_x, current_y + move_y
                if (
                    maze.in_grid(next_x, next_y)
                    and not maze.is_solid(next_x, next_y)
                    and maze.has_wall(current_x, current_y, bit)
                ):
                    closed_neighbors.append((next_x, next_y, bit, opp_bit))

            if closed_neighbors:
                next_x, next_y, bit, opp_bit = random.choice(closed_neighbors)
                maze.break_wall(
                    current_x, current_y, bit, opp_bit, next_x, next_y
                )

                if animation:
                    animation(maze, delay)
