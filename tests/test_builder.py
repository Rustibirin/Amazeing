"""Unit tests for the Builder module and maze generation logic."""

import pytest
from maze import Maze
from builder import Builder


@pytest.fixture
def maze_settings() -> dict[str, object]:
    """Returns standard maze settings for testing builder logic."""
    return {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "PERFECT": True,
    }


def test_builder_different_seeds_produce_different_mazes(
    maze_settings: dict[str, object]
) -> None:
    """Test that different seeds produce different maze structures."""
    maze_a = Maze(maze_settings)
    maze_b = Maze(maze_settings)

    builder_a = Builder(seed=11111)
    builder_b = Builder(seed=99999)

    builder_a.build(maze_a, perfect=True, delay=0.0)
    builder_b.build(maze_b, perfect=True, delay=0.0)

    assert maze_a.matrix != maze_b.matrix


def test_perfect_maze_all_valid_cells_marked_in_maze(
    maze_settings: dict[str, object]
) -> None:
    """Test that Wilson's algorithm processes every non-solid cell."""
    maze = Maze(maze_settings)
    builder = Builder(seed=42)
    builder.build(maze, perfect=True, delay=0.0)

    for y in range(maze.height):
        for x in range(maze.width):
            if not maze.is_solid(x, y):
                assert maze.in_maze(x, y) is True


def test_pacman_mode_modifies_walls(
    maze_settings: dict[str, object]
) -> None:
    """Test that non-perfect mode (Pac-Man) breaks extra walls."""
    maze_perfect = Maze(maze_settings)
    maze_imperfect = Maze(maze_settings)

    builder_perfect = Builder(seed=42)
    builder_imperfect = Builder(seed=42)

    builder_perfect.build(maze_perfect, perfect=True, delay=0.0)
    builder_imperfect.build(
        maze_imperfect, perfect=False, delay=0.0, game_mode=1.0
    )

    assert maze_perfect.matrix != maze_imperfect.matrix


def test_builder_animation_callback(
    maze_settings: dict[str, object]
) -> None:
    """Test that the animation callback is executed during generation."""
    maze = Maze(maze_settings)
    builder = Builder(seed=42)
    steps_count = 0

    def mock_callback(m: Maze, delay: float) -> None:
        nonlocal steps_count
        steps_count += 1

    builder.build(maze, perfect=True, delay=0.0, animation=mock_callback)
    assert steps_count > 0
