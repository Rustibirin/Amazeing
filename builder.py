"""Maze generation and pathfinding engine."""

import random
from typing import Any, Callable, Dict, Tuple


class Builder:
    """
    Handles maze generation logic using
    Wilson's algorithm and Pac-Man mode.
    """

    def __init__(self, seed: int | None = None) -> None:
        """
        Initializes the Builder instance with a specific random seed.

        Args:
            seed: Seed value for random number generator reproducibility.
        """
        if seed is None:
            seed = random.randint(1, 2**31 - 1)

        self.seed = seed
        random.seed(self.seed)
        self._animation: Callable[[Any, float], None] | None = None
        self._delay: float = 0.0
        self._was_interrupted: bool = False

    def build(
        self,
        maze: Any,
        perfect: bool,
        delay: float,
        difficulty: float | Any = 1,
        animation: Callable[[Any, float], None] | None = None,
        algorithm: str = "wilson"
    ) -> None:
        """
        Executes the maze generation pipeline.

        If keyboard interruption occurs during rendering, animation is disabled
        and generation completes synchronously.

        Args:
            maze: The maze grid object to be constructed.
            perfect: If True, generates a perfect maze; otherwise adds loops.
            delay: Delay in seconds between rendering animation steps.
            difficulty: Factor to breaking walls in non-perfect mode.
            animation: Optional callback for step-by-step rendering.
            start_cell: Coordinates of the entry cell.
            exit_cell: Coordinates of the exit cell.

        Raises:
            KeyboardInterrupt: If generation was interrupted by user input.
        """
        self._animation = animation
        self._delay = delay
        self._was_interrupted = False

        if algorithm == "wilson":
            self._perfect_maze_by_wilson(maze)
        else:
            self._perfect_maze_by_DFS(maze)

        if not perfect:
            self._pacman_mode(maze, difficulty)

        if self._was_interrupted:
            raise KeyboardInterrupt

    def _render_step(self, maze: Any) -> None:
        """
        Executes a single animation step and
        safely handles keyboard interrupts.

        Args:
            maze: The current maze instance.
        """
        if self._animation:
            try:
                self._animation(maze, self._delay)
            except KeyboardInterrupt:
                self._animation = None
                self._delay = 0.0
                self._was_interrupted = True

    def _perfect_maze_by_wilson(self, maze: Any) -> None:
        """
        Generates a perfect maze with no loops using Wilson's algorithm.

        Args:
            maze: The maze grid object to alter.
        """
        start_cell = maze.entry
        exit_cell = maze.exit
        valid_grid: list[Tuple[int, int]] = [
            (x, y)
            for x in range(maze.width)
            for y in range(maze.height)
            if not maze.is_solid(x, y)
        ]

        if not valid_grid:
            return

        force_exit_start = True if exit_cell in valid_grid else False

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

            if force_exit_start and exit_cell in unvisited:
                walk_start = exit_cell
                force_exit_start = False
            else:
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

                self._render_step(maze)

                cell_ptr = next_cell

    def _perfect_maze_by_DFS(self, maze: Any) -> None:
        """
        Generates a perfect maze with no loops
        using an Iterative Depth-First Search.

        Args:
            maze: The maze grid object to alter.
        """
        start_cell = maze.entry
        visited: set[tuple[int, int]] = {start_cell}

        maze.mark_in_maze(start_cell[0], start_cell[1])
        stack: list[tuple[int, int]] = [start_cell]

        while stack:
            current_x, current_y = stack[-1]

            unvisited_neighbors = []
            for move_x, move_y, bit, opp_bit in maze.DIR_MAP.values():
                next_x, next_y = current_x + move_x, current_y + move_y
                if (
                    maze.in_grid(next_x, next_y)
                    and (next_x, next_y) not in visited
                    and not maze.is_solid(next_x, next_y)
                ):
                    unvisited_neighbors.append((next_x, next_y, bit, opp_bit))

            if unvisited_neighbors:
                next_x, next_y, bit, opp_bit = random.choice(
                    unvisited_neighbors
                )
                maze.break_wall(
                    current_x, current_y, bit, opp_bit, next_x, next_y
                )

                maze.mark_in_maze(next_x, next_y)
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
                self._render_step(maze)
            else:
                stack.pop()

    def _pacman_mode(self, maze: Any, difficulty: float) -> None:
        """
        Transforms a perfect maze into an imperfect maze by adding loops.

        Args:
            maze: The maze grid object.
            difficulty: Imperfection multiplier affecting wall removal density.
        """
        self._open_corners(maze)
        self._break_dead_ends(maze, difficulty)

    def _open_corners(self, maze: Any) -> None:
        """
        Opens outer wall corners of the maze to enable Pac-Man style passages.

        Args:
            maze: The maze grid object.
        """
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
                            self._render_step(maze)

    def _break_dead_ends(self, maze: Any, difficulty: float) -> None:
        """
        Removes random walls from dead ends
        based on game mode ratio to introduce loops.

        Args:
            maze: The maze grid object.
            difficulty: Ratio (0.0 to 1.0) of dead ends to break.
        """
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
        ends_to_break = int(len(dead_ends) * difficulty)
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
                self._render_step(maze)
