"""Reusable Maze Generator Module for external integration."""

from pydantic import BaseModel, Field, PrivateAttr, model_validator

from mazegen.maze import Maze
from mazegen.builder import Builder
from mazegen.solver import Solver
from mazegen.exporter import Exporter
from mazegen.parser import Difficulty

from typing import Any, Callable


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

        for key in ('WIDTH', 'HEIGHT'):
            val = self.settings.get(key)
            if not (isinstance(val, int) and val):
                raise ValueError(f"Invalid '{key}': Must be an integer.")

        for key in ('ENTRY', 'EXIT'):
            val = self.settings.get(key)
            if (not isinstance(val, tuple)
               or len(val) != 2
               or not isinstance(val[0], int)
               or not isinstance(val[1], int)):
                raise ValueError(
                    f"Invalid '{key}': Must be a tuple of two integers."
                )

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
                    "hard, insane)."
                )
            self.settings['DIFFICULTY'] = diff

        if 'DELAY' in self.settings:
            delay = self.settings['DELAY']

            if not isinstance(delay, (int, float)):
                raise ValueError(f"Invalid DELAY: '{delay}'. "
                                 "Must be int or float.")

        if 'SEED' in self.settings:
            seed = self.settings['SEED']

            if not isinstance(seed, int):
                raise ValueError(f"Invalid SEED: '{seed}'. "
                                 "Must be int.")

        return self

    _maze: Maze | None = PrivateAttr(default=None)
    _solution: str | None = PrivateAttr(default=None)

    @model_validator(mode='after')
    def validate_bounds_and_positions(self) -> 'MazeGenerator':
        """
        Validate dinamically the coordinates and sizes.
        """
        width = self.settings['WIDTH']
        height = self.settings['HEIGHT']

        if width < 4 or height < 4:
            raise ValueError(
                "The width and height of the maze must be at least 4 "
                "cells for each dimension."
            )

        if self.settings['ENTRY'] == self.settings['EXIT']:
            raise ValueError(
                "The 'ENTRY' and 'EXIT' coordinates must be different."
            )

        for key in ('ENTRY', 'EXIT'):
            x, y = self.settings[key]
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"'{key}' {(x, y)} is out of bounds for maze size "
                    f"{width}x{height}."
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
        builder = Builder(seed=self.settings.get('SEED', None))
        difficulty_val = self.settings.get("DIFFICULTY", Difficulty.BONUS)

        try:
            builder.build(
                self._maze,
                perfect=self.settings['PERFECT'],
                delay=delay,
                difficulty=difficulty_val,
                animation=animation,
                algorithm=self.settings.get("ALGORITHM", "WILSON")
            )
        except KeyboardInterrupt:
            builder.build(
                self._maze,
                perfect=self.settings["PERFECT"],
                delay=delay,
                difficulty=difficulty_val,
                animation=None,
                algorithm=self.settings.get("ALGORITHM", "WILSON")
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
