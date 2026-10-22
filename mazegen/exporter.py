"""Maze File Exporter Module."""

from pathlib import Path
from typing import Any


class Exporter:
    """
    Handles saving the maze structure and solution path to a text file
    adhering to 42 project specifications.
    """

    @staticmethod
    def export(maze: Any, solution: str, filepath: str | Path) -> None:
        """
        Exports the maze grid in hexadecimal format along with entry, exit,
        and solution path to a file.

        Args:
            maze: The maze instance containing dimensions,
            wall masks, entry, and exit.
            solution: String sequence representing
            the solution directions (e.g., "NNEESW").
            filepath: Target output file path.

        Raises:
            OSError: If directory creation or file writing fails.
        """
        path = Path(filepath)

        if path.parent:
            path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []

        for y in range(maze.height):
            row: list[str] = []
            for x in range(maze.width):
                wall_mask = maze.get_wall_mask(x, y)
                row.append(f"{wall_mask:X}")
            lines.append("".join(row))

        lines.append("")
        lines.append(f"{maze.entry[0]},{maze.entry[1]}")
        lines.append(f"{maze.exit[0]},{maze.exit[1]}")
        lines.append(solution)

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
