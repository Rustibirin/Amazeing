"""Maze Pathfinding Solver Module."""

from collections import deque
from typing import Any


class Solver:
    """
    Calculates the shortest path in a maze using the BFS algorithm.
    """

    def solve(self, maze: Any) -> str:
        """
        Finds the shortest path sequence from entry to exit.
        Args:
            maze: Instance of the Maze model.
        Returns:
            str: Optimal path sequence (e.g., "NNEESSW").
        Raises:
            ValueError: If no accessible path exists between entry and exit.
        """

        start_x, start_y = maze.entry
        target = maze.exit

        queue: deque[tuple[int, int, str]] = deque([(start_x, start_y, "")])
        maze.mark_visited(start_x, start_y)

        try:
            while queue:
                current_x, current_y, path = queue.popleft()

                if (current_x, current_y) == target:
                    return path

                for label, (move_x, move_y, bit, _) in maze.DIR_MAP.items():
                    if not maze.has_wall(current_x, current_y, bit):
                        next_x, next_y = current_x + move_x, current_y + move_y

                        if (
                            maze.in_grid(next_x, next_y)
                            and not maze.is_solid(next_x, next_y)
                            and not maze.is_visited(next_x, next_y)
                        ):
                            maze.mark_visited(next_x, next_y)
                            queue.append((next_x, next_y, path + label))

            raise ValueError("No valid path found between ENTRY and EXIT.")

        finally:
            self._reset_visited_flags(maze)

    def _reset_visited_flags(self, maze: Any) -> None:
        """
        Clears VISITED bit flags consumed during the pathfinding search.
        """

        for y in range(maze.height):
            for x in range(maze.width):
                if maze.is_visited(x, y):
                    maze.clear_visited(x, y)
