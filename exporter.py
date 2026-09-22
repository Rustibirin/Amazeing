"""Maze File Exporter Module."""

from typing import Any


class Exporter:
    """Handles saving the maze to a text file adhering to 42 subject specs."""

    @staticmethod
    def export(
        maze: Any,
        solution: str,
        filepath: str,
    ) -> None:
        """Writes hex grid, empty line, entry, exit, and solution path."""
        lines: list[str] = []

        for y in range(maze.height):
            row: list[str] = []
            for x in range(maze.width):
                wall_mask = maze.get_wall_mask(x, y)
                hex_digit = f"{wall_mask:X}"
                row.append(hex_digit)
            lines.append("".join(row))

        lines.append("")
        lines.append(f"{maze.entry[0]},{maze.entry[1]}")
        lines.append(f"{maze.exit[0]},{maze.exit[1]}")
        lines.append(solution)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
