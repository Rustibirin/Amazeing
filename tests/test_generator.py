"""Unit tests for the MazeGenerator facade class and high-level API."""

from pathlib import Path
import pytest
from generator import MazeGenerator
from maze import Maze


@pytest.fixture
def valid_settings(tmp_path: Path) -> dict[str, object]:
    """Returns valid settings dictionary using a temporary output file."""
    return {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "PERFECT": True,
        "SEED": 42,
        "OUTPUT_FILE": str(tmp_path / "maze.txt"),
    }


def test_generator_initialization(valid_settings: dict[str, object]) -> None:
    """Test initial state of MazeGenerator."""
    generator = MazeGenerator(valid_settings)
    assert generator.maze is None
    assert generator.solution is None
    assert generator.settings == valid_settings


def test_generator_generate(valid_settings: dict[str, object]) -> None:
    """Test maze generation produces a valid Maze instance."""
    generator = MazeGenerator(valid_settings)
    maze = generator.generate()

    assert isinstance(maze, Maze)
    assert generator.maze is maze
    assert maze.width == 10
    assert maze.height == 10


def test_generator_solve(valid_settings: dict[str, object]) -> None:
    """Test pathfinding solution generation after maze creation."""
    generator = MazeGenerator(valid_settings)
    generator.generate()
    solution = generator.solve()

    assert isinstance(solution, str)
    assert len(solution) > 0
    assert generator.solution == solution


def test_generator_solve_before_generate_raises_runtime_error(
    valid_settings: dict[str, object]
) -> None:
    """Test that calling solve() before generate() raises RuntimeError."""
    generator = MazeGenerator(valid_settings)
    with pytest.raises(RuntimeError, match="must be generated before solving"):
        generator.solve()


def test_generator_export(valid_settings: dict[str, object]) -> None:
    """Test exporting maze to default output path."""
    generator = MazeGenerator(valid_settings)
    generator.generate()
    generator.solve()
    generator.export()

    output_path = Path(str(valid_settings["OUTPUT_FILE"]))
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generator_export_before_steps_raises_runtime_error(
    valid_settings: dict[str, object]
) -> None:
    """Test that exporting before generating or solving raises RuntimeError."""
    generator = MazeGenerator(valid_settings)

    with pytest.raises(
        RuntimeError, match="must be generated and solved before exporting"
    ):
        generator.export()

    generator.generate()
    with pytest.raises(
        RuntimeError, match="must be generated and solved before exporting"
    ):
        generator.export()
