"""Unit tests for the Exporter module and maze file format specifications."""

from pathlib import Path
import pytest
from mazegen.maze import Maze
from mazegen.exporter import Exporter


@pytest.fixture
def maze_setup() -> Maze:
    """Returns a configured 3x3 maze instance with known broken walls."""
    settings = {
        "WIDTH": 3,
        "HEIGHT": 3,
        "ENTRY": (0, 0),
        "EXIT": (2, 2),
        "PERFECT": True,
    }
    maze = Maze(settings)

    maze.break_wall(0, 0, Maze.EAST, Maze.WEST, 1, 0)
    return maze


def test_exporter_file_structure_and_content(
    maze_setup: Maze, tmp_path: Path
) -> None:
    """Test exported file structure, line count, coordinates, and solution."""
    output_file = tmp_path / "exported_maze.txt"
    solution = "EESS"

    Exporter.export(maze_setup, solution, str(output_file))

    assert output_file.exists()
    lines = output_file.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 7

    assert lines[3] == ""

    assert lines[4] == "0,0"
    assert lines[5] == "2,2"
    assert lines[6] == "EESS"


def test_exporter_hex_formatting(
    maze_setup: Maze, tmp_path: Path
) -> None:
    """
    Test that cell wall masks are formatted as uppercase hexadecimal digits.
    """

    output_file = tmp_path / "hex_test.txt"
    Exporter.export(maze_setup, "E", str(output_file))

    lines = output_file.read_text(encoding="utf-8").splitlines()
    first_row = lines[0]

    assert len(first_row) == 3

    assert first_row[0] == "D"
    assert first_row[1] == "7"
    assert first_row[2] == "F"


def test_exporter_empty_solution(
    maze_setup: Maze, tmp_path: Path
) -> None:
    """Test exporting when solution string is empty."""
    output_file = tmp_path / "empty_sol.txt"
    Exporter.export(maze_setup, "", str(output_file))

    lines = output_file.read_text(encoding="utf-8").splitlines()
    assert lines[6] == ""


def test_exporter_trailing_newline(
    maze_setup: Maze, tmp_path: Path
) -> None:
    """Test that the exported file ends with a trailing newline."""
    output_file = tmp_path / "newline_test.txt"
    Exporter.export(maze_setup, "EESS", str(output_file))

    raw_text = output_file.read_text(encoding="utf-8")
    assert raw_text.endswith("\n")
