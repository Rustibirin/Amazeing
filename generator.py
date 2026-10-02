"""Reusable Maze Generator Module for external integration."""

from typing import Any, Callable
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from maze import Maze
from builder import Builder
from solver import Solver
from exporter import Exporter
from parser import Difficulty


class MazeGenerator(BaseModel):
    """
    High-level reusable generator class that orchestrates
    maze creation, pathfinding search, and file exporting.
    """

    settings: dict[str, Any] = Field(
        ...,
        description="The whole settings of the maze"
    )

    @model_validator(mode='after')
    def validate_types(self) -> 'MazeGenerator':
        if (not (isinstance(self.settings.get('WIDTH'), int)
                 and self.settings.get('WIDTH'))):
            raise ValueError("Invalid 'WIDTH' must be an integer.")

        if (not (isinstance(self.settings.get('HEIGHT'), int)
                 and self.settings.get('HEIGHT'))):
            raise ValueError("Invalid 'HEIGHT' must be an integer.")

        if (not isinstance(self.settings.get('ENTRY'), tuple)
           or len(self.settings['ENTRY']) != 2
           or not isinstance(self.settings['ENTRY'][0], int)
           or not isinstance(self.settings['ENTRY'][1], int)):
            raise ValueError("Invalid 'ENTRY' must be a tuple of two"
                             " integers.")

        if (not isinstance(self.settings.get('EXIT'), tuple)
           or len(self.settings['EXIT']) != 2
           or not isinstance(self.settings['EXIT'][0], int)
           or not isinstance(self.settings['EXIT'][1], int)):
            raise ValueError("Invalid 'EXIT' must be a tuple of two integers.")

        if (not (isinstance(self.settings.get('OUTPUT_FILE'), str)
                 and self.settings.get('OUTPUT_FILE'))):
            raise ValueError("The name of the 'OUTPUT_FILE' must be a string.")

        if not isinstance(self.settings.get('PERFECT'), bool):
            raise ValueError("'PERFECT' maze must be a boolean.")

        if 'ALGORITHM' in self.settings:
            if not isinstance(self.settings['ALGORITHM'], str):
                raise ValueError("ALGORITHM must be a string.")

            val_algorithm = self.settings['ALGORITHM'].upper()
            if val_algorithm not in ('WILSON', 'DFS'):
                raise ValueError("ALGORITHM must be 'WILSON' or 'DFS'.")

            self.settings['ALGORITHM'] = val_algorithm

        if 'DIFFICULTY' in self.settings:
            diff = self.settings['DIFFICULTY']

            if isinstance(diff, str):
                try:
                    diff = Difficulty[diff.upper()]
                except KeyError:
                    valid_diffs = ('bonus', 'easy', 'medium', 'hard', 'insane')
                    raise ValueError(
                        f"Invalid DIFFICULTY '{diff}'. Must be one of: "
                        f"{valid_diffs}"
                    )
            elif not isinstance(diff, Difficulty):
                raise ValueError(
                    "DIFFICULTY must be a word (bonus, easy, medium, "
                    "hard, insane) or a Difficulty Enum."
                )
            self.settings['DIFFICULTY'] = diff

        if 'DELAY' in self.settings:
            delay = self.settings['DELAY']

            if not (isinstance(delay, (int, float))):
                raise ValueError(f"Invalid DELAY: '{delay}'. "
                                 "Must be a number.")

        if 'SEED' in self.settings:
            seed = self.settings['SEED']

            if not (isinstance(seed, (int))):
                raise ValueError(f"Invalid SEED: '{seed}'. "
                                 "Must be an integer.")

        return self

    _maze: Maze | None = PrivateAttr(default=None)
    _solution: str | None = PrivateAttr(default=None)

    @model_validator(mode='after')
    def validate_bounds_and_positions(self) -> 'MazeGenerator':
        """
        Validate dinamically the coordinates and sizes.
        """

        if (self.settings['WIDTH'] < 4 or self.settings['HEIGHT'] < 4):
            msg: str = "The width and height of the maze must be at least 4"
            raise ValueError(f"{msg} cells for each dimension.")

        entry_cell = self.settings['ENTRY']
        exit_cell = self.settings['EXIT']
        if entry_cell == exit_cell:
            text = "The 'ENTRY' and 'EXIT' coordinates must"
            raise ValueError(f"{text} be different.")

        entry_x, entry_y = entry_cell
        if not (0 <= entry_x < self.settings['WIDTH']
                and 0 <= entry_y < self.settings['HEIGHT']):
            msg = f"'ENTRY' {entry_cell} is out of bounds for maze size"
            raise ValueError(
                f"{msg} {self.settings['WIDTH']}x{self.settings['HEIGHT']}."
            )

        exit_x, exit_y = exit_cell
        if not (0 <= exit_x < self.settings['WIDTH']
                and 0 <= exit_y < self.settings['HEIGHT']):
            msg = f"'EXIT' {exit_cell} is out of bounds for maze size"
            raise ValueError(
                f"{msg} {self.settings['WIDTH']}x{self.settings['HEIGHT']}."
            )

        return self

    @property
    def maze(self) -> Maze | None:
        """Access to read the object Maze."""
        return self._maze

    @property
    def solution(self) -> str | None:
        """Access to read the solution."""
        return self._solution

    def generate(
        self,
        animation: Callable[[Any, float], None] | None = None,
        delay: float = 0.0,
    ) -> tuple[Maze, bool]:
        """Generates the maze structure using the configured parameters.

        Returns:
            tuple[Maze, bool]: The constructed maze and animation status.
        """
        self._maze = Maze(self.settings)
        builder = Builder(seed=self.settings.get('SEED'))

        difficulty_attr = self.settings.get('DIFFICULTY', Difficulty.BONUS)
        difficulty_val = (
            difficulty_attr.value
            if hasattr(difficulty_attr, 'value')
            else difficulty_attr
        )

        try:
            builder.build(
                self._maze,
                perfect=self.settings['PERFECT'],
                delay=delay,
                difficulty=difficulty_val,
                animation=animation,
                algorithm=self.settings.get('ALGORITHM', 'WILSON').upper()
            )
        except KeyboardInterrupt:
            builder.build(
                self._maze,
                perfect=self.settings["PERFECT"],
                delay=delay,
                difficulty=difficulty_val,
                animation=None,
                algorithm=self.settings.get('ALGORITHM', 'WILSON').upper()
            )
            raise KeyboardInterrupt

        assert self._maze is not None
        return (self._maze, animation is not None)

    def solve(self) -> str:
        """Calculates the shortest path solution from entry to exit."""
        if self._maze is None:
            raise RuntimeError("Maze must be generated before solving.")

        solver = Solver()
        self._solution = solver.solve(self._maze)
        return self._solution

    def export(self) -> None:
        """
        Exports the hex grid, coordinates, and solution path to a text file.
        """
        if self._maze is None or self._solution is None:
            raise RuntimeError(
                "Maze must be generated and solved before exporting."
            )

        Exporter.export(
            self._maze,
            self._solution,
            self.settings['OUTPUT_FILE']
        )
