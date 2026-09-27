"""Reusable Maze Generator Module for external integration."""

from typing import Any, Callable, Tuple
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from maze import Maze
from builder import Builder
from solver import Solver
from exporter import Exporter
from parser import GameMode


class MazeGenerator(BaseModel):
    """High-level reusable generator class that orchestrates
    maze creation, pathfinding search, and file exporting.
    """
    settings: dict[str, str | Any] = Field(
        ...,
        description="The whole settings of the maze"
    )

    @model_validator(mode='after')
    def validate_types(self) -> 'MazeGenerator':
        if (not isinstance(self.settings.get('WIDTH'), int)):
            raise ValueError("Invalid width must be an integer.")

        if (not isinstance(self.settings.get('HEIGHT'), int)):
            raise ValueError("Invalid height must be an integer.")

        if (not isinstance(self.settings.get('ENTRY'), tuple)
            or len(self.settings.get('ENTRY')) != 2
            or not isinstance(self.settings.get('ENTRY')[0], int)
            or not isinstance(self.settings.get('ENTRY')[1], int)
           ):
            raise ValueError("Invalid entry must be a tuple of two integers.")

        if (not isinstance(self.settings.get('EXIT'), tuple)
            or len(self.settings.get('EXIT')) != 2
            or not isinstance(self.settings.get('EXIT')[0], int)
            or not isinstance(self.settings.get('EXIT')[1], int)
           ):
            raise ValueError("Invalid exit must be a tuple of two integers.")

        if (not isinstance(self.settings.get('OUTPUT_FILE'), str)):
            raise ValueError("The name of the output file must be a string.")

        if (not isinstance(self.settings.get('PERFECT'), bool)):
            raise ValueError("Im/perfect maze must be a boolean.")

        return self

    _maze: Maze | None = PrivateAttr(default=None)
    _solution: str | None = PrivateAttr(default=None)

    @model_validator(mode='after')
    def validate_bounds_and_positions(self) -> 'MazeGenerator':
        """Valida dinámicamente las coordenadas según width y height."""
        if (self.settings['WIDTH'] < 4 or self.settings['HEIGHT'] < 4):
            msg: str = "The widht and height of the maze must be at least 4"
            raise ValueError(f"{msg} cells for each dimension.")

        entry_cell = self.settings['ENTRY']
        exit_cell = self.settings['EXIT']
        if entry_cell == exit_cell:
            raise ValueError("The 'entry' and 'exit' coordinates must be different.")

        entry_x, entry_y = entry_cell
        if not (0 <= entry_x < self.settings['WIDTH']
                and 0 <= entry_y < self.settings['HEIGHT']):
            msg: str = f"'entry' {entry_cell} is out of bounds for maze size"
            raise ValueError(
                f"{msg} {self.settings['WIDTH']}x{self.settings['HEIGHT']}."
            )

        
        exit_x, exit_y = exit_cell
        if not (0 <= exit_x < self.settings['WIDTH']
                and 0 <= exit_y < self.settings['HEIGHT']):
            msg: str = f"'exit' {exit_cell} is out of bounds for maze size"
            raise ValueError(
                f"{msg} {self.settings['WIDTH']}x{self.settings['HEIGHT']}."
            )

        return self

    @property
    def maze(self) -> Maze | None:
        """Acceso de lectura al objeto Maze."""
        return self._maze

    @property
    def solution(self) -> str | None:
        """Acceso de lectura a la solución."""
        return self._solution

    def generate(
        self,
        animation: Callable[[Any, float], None] | None = None,
        delay: float = 0.0,
    ) -> Tuple[Maze, bool]:
        """Generates the maze structure using the configured parameters.

        Returns:
            Tuple[Maze, bool]: The constructed maze instance and animation status.
        """
        self._maze = Maze(self.settings)
        
        builder = Builder(seed=self.settings.get('SEED'))

        try:
            builder.build(
                self._maze,
                perfect=self.settings['PERFECT'],
                delay=delay,
                game_mode=self.settings.get('GAME_MODE') or GameMode.BONUS,
                animation=animation,
                start_cell=self.settings['ENTRY'],
                exit_cell=self.settings['EXIT']
            )
        except KeyboardInterrupt:
            raise KeyboardInterrupt

        return (self._maze, animation is not None)

    def solve(self) -> str:
        """Calculates the shortest path solution from entry to exit."""
        if self._maze is None:
            raise RuntimeError("Maze must be generated before solving.")

        solver = Solver()
        self._solution = solver.solve(self._maze)
        return self._solution

    def export(self) -> None:
        """Exports the hex grid, coordinates, and solution path to a text file."""
        if self._maze is None or self._solution is None:
            raise RuntimeError(
                "Maze must be generated and solved before exporting."
            )

        Exporter.export(self._maze, self._solution, 
                        self.settings['OUTPUT_FILE'])