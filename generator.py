"""Reusable Maze Generator Module for external integration."""

from typing import Any, Callable
from maze import Maze
from builder import Builder
from solver import Solver
from exporter import Exporter
from configuration import GameMode


class MazeGenerator:
    """High-level reusable generator class that orchestrates
    maze creation, pathfinding search, and file exporting.
    """

    def __init__(
            self,
            settings: dict[str, Any]
    ) -> None:
        self.settings: dict[str, Any] = settings
        self.maze: Maze | None = None
        self.solution: str | None = None

    def generate(
        self,
        animation: Callable[[Any, float], None] | None = None,
        delay: float = 0.0,
    ) -> Maze:
        """Generates the maze structure using the configured parameters.

        Returns:
            Maze: The constructed maze instance.
        """
        self.maze = Maze(self.settings)
        builder = Builder(seed=self.settings.get("SEED"))
        builder.build(
            self.maze,
            perfect=self.settings["PERFECT"],
            delay=delay,
            game_mode=self.settings.get("GAME_MODE", GameMode.BONUS).value,
            animation=animation,
        )
        return self.maze

    def solve(self) -> str:
        """Calculates the shortest path solution from entry to exit.

        Returns:
            str: Sequence of movement directions (e.g. 'NNEESW').

        Raises:
            RuntimeError: If called before generating the maze.
        """
        if self.maze is None:
            raise RuntimeError("Maze must be generated before solving.")

        solver = Solver()
        self.solution = solver.solve(self.maze)
        return self.solution

    def export(self) -> None:
        """Exports the hex grid, coordinates, and solution path to a text file.

        Raises:
            RuntimeError: If called before maze generation or path solving.
        """
        if self.maze is None or self.solution is None:
            raise RuntimeError(
                "Maze must be generated and solved before exporting."
            )

        Exporter.export(self.maze, self.solution, self.settings["OUTPUT_FILE"])
