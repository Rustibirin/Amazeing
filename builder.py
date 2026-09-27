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
        game_mode: float = 1,
        animation: Callable[[Any, float], None] | None = None,
        start_cell: tuple[int, int] = (0, 0),
        exit_cell: tuple[int, int] = (1, 1)
    ) -> None:
        """
        Executes the maze generation pipeline.
        
        Completa SIEMPRE el laberinto al 100%. Si ocurre un KeyboardInterrupt
        durante la animación, desactiva la animación, termina todo el proceso
        e interrumpe al final lanzando KeyboardInterrupt.
        """
        if game_mode is None:
            game_mode = 1.0
        elif hasattr(game_mode, 'value'):
            game_mode = float(game_mode.value)
        else:
            game_mode = float(game_mode)
        was_interrupted = False

        animation, delay, interrupted = self._create_perfect_maze(
            maze, animation, delay, start_cell, exit_cell
        )
        if interrupted:
            was_interrupted = True

        if not perfect:
            animation, delay, interrupted = self._pacman_mode(
                maze, delay, game_mode, animation
            )
            if interrupted:
                was_interrupted = True

        if was_interrupted:
            raise KeyboardInterrupt

    def _render_step(
        self,
        maze: Any,
        animation: Callable[[Any, float], None] | None,
        delay: float
    ) -> Tuple[Callable[[Any, float], None] | None, float, bool]:
        """
        Ejecuta la animación. Si salta Ctrl+C, desactiva la animación
        pero devuelve una bandera para continuar el algoritmo sin pausas.
        """
        if animation:
            try:
                animation(maze, delay)
            except KeyboardInterrupt:
                return None, 0.0, True
        return animation, delay, False

    def _create_perfect_maze(
        self,
        maze: Any,
        animation: Callable[[Any, float], None] | None,
        delay: float,
        start_cell: tuple[int, int],
        exit_cell: tuple[int, int]
    ) -> Tuple[Callable[[Any, float], None] | None, float, bool]:
        valid_grid: list[Tuple[int, int]] = [
            (x, y)
            for x in range(maze.width)
            for y in range(maze.height)
            if not maze.is_solid(x, y)
        ]

        was_interrupted = False
        if not valid_grid:
            return animation, delay, was_interrupted

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

                # Renderizar paso
                animation, delay, interrupted = self._render_step(
                    maze, animation, delay
                )
                if interrupted:
                    was_interrupted = True

                cell_ptr = next_cell

        return animation, delay, was_interrupted

    def _pacman_mode(
        self,
        maze: Any,
        delay: float,
        game_mode: float,
        animation: Callable[[Any, float], None] | None,
    ) -> Tuple[Callable[[Any, float], None] | None, float, bool]:
        was_interrupted = False

        animation, delay, interrupted_corners = self._open_corners(
            maze, delay, animation
        )
        if interrupted_corners:
            was_interrupted = True

        animation, delay, interrupted_ends = self._break_dead_ends(
            maze, game_mode, delay, animation
        )
        if interrupted_ends:
            was_interrupted = True

        return animation, delay, was_interrupted

    def _open_corners(
        self,
        maze: Any,
        delay: float,
        animation: Callable[[Any, float], None] | None,
    ) -> Tuple[Callable[[Any, float], None] | None, float, bool]:
        was_interrupted = False
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
                            animation, delay, interrupted = self._render_step(
                                maze, animation, delay
                            )
                            if interrupted:
                                was_interrupted = True

        return animation, delay, was_interrupted

    def _break_dead_ends(
        self,
        maze: Any,
        game_mode: float,
        delay: float,
        animation: Callable[[Any, float], None] | None,
    ) -> Tuple[Callable[[Any, float], None] | None, float, bool]:
        """breaks dead ends by tearing down extra walls, creating loops."""
        was_interrupted = False
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
                animation, delay, interrupted = self._render_step(
                    maze, animation, delay
                )
                if interrupted:
                    was_interrupted = True

        return animation, delay, was_interrupted