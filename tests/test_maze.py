"""Unit tests for the Maze model and bitwise matrix operations."""

import pytest
from maze import Maze
from typing import Any


@pytest.fixture
def default_settings() -> dict[str, Any]:
    """Returns standard maze settings for testing."""
    return {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "PERFECT": True,
    }


def test_maze_initialization(default_settings: dict[str, object]) -> None:
    """Test initial maze state, matrix dimensions, and wall masks."""
    maze = Maze(default_settings)
    assert maze.width == 10
    assert maze.height == 10
    assert maze.entry == (0, 0)
    assert maze.exit == (9, 9)
    assert len(maze.matrix) == 10
    assert len(maze.matrix[0]) == 10

    for y in range(maze.height):
        for x in range(maze.width):
            if not maze.is_solid(x, y):
                assert maze.get_wall_mask(x, y) == Maze.ALL_WALLS_MASK


def test_in_grid(default_settings: dict[str, object]) -> None:
    """Test boundary checking method in_grid."""
    maze = Maze(default_settings)
    assert maze.in_grid(0, 0) is True
    assert maze.in_grid(9, 9) is True
    assert maze.in_grid(-1, 0) is False
    assert maze.in_grid(0, -1) is False
    assert maze.in_grid(10, 0) is False
    assert maze.in_grid(0, 10) is False


def test_bitwise_in_maze(default_settings: dict[str, object]) -> None:
    """Test marking and checking IN_MAZE bit flag."""
    maze = Maze(default_settings)
    assert maze.in_maze(2, 2) is False
    maze.mark_in_maze(2, 2)
    assert maze.in_maze(2, 2) is True


def test_bitwise_solid(default_settings: dict[str, object]) -> None:
    """Test marking and checking SOLID bit flag."""
    maze = Maze(default_settings)
    assert maze.is_solid(2, 2) is False
    maze.mark_solid(2, 2)
    assert maze.is_solid(2, 2) is True


def test_bitwise_visited(default_settings: dict[str, object]) -> None:
    """Test marking, checking, and clearing VISITED bit flag."""
    maze = Maze(default_settings)
    assert maze.is_visited(3, 3) is False
    maze.mark_visited(3, 3)
    assert maze.is_visited(3, 3) is True

    maze.clear_visited(3, 3)
    assert maze.is_visited(3, 3) is False


def test_wall_operations(default_settings: dict[str, object]) -> None:
    """Test wall inspection and symmetric wall breaking."""
    maze = Maze(default_settings)
    x, y = 4, 4
    nx, ny = 5, 4  # Move East

    assert maze.has_wall(x, y, Maze.EAST) is True
    assert maze.has_wall(nx, ny, Maze.WEST) is True

    maze.break_wall(x, y, Maze.EAST, Maze.WEST, nx, ny)

    assert maze.has_wall(x, y, Maze.EAST) is False
    assert maze.has_wall(nx, ny, Maze.WEST) is False


def test_can_stamp_symbol(default_settings: dict[str, object]) -> None:
    """Test stamping check for embedded templates."""
    maze = Maze(default_settings)
    small_symbol = [[1, 1], [1, 1]]
    large_symbol = [[1] * 15 for _ in range(15)]

    assert maze.can_stamp_symbol(small_symbol) is True
    assert maze.can_stamp_symbol(large_symbol) is False
    assert maze.can_stamp_symbol([]) is False


def test_has_42_flag_behavior() -> None:
    """Test has_42 flag activation depending on maze dimensions."""
    small_settings = {
        "WIDTH": 5,
        "HEIGHT": 5,
        "ENTRY": (0, 0),
        "EXIT": (4, 4),
        "PERFECT": True,
    }
    small_maze = Maze(small_settings)
    assert small_maze.has_42 is False

    large_settings = {
        "WIDTH": 20,
        "HEIGHT": 20,
        "ENTRY": (0, 0),
        "EXIT": (19, 19),
        "PERFECT": True,
    }
    large_maze = Maze(large_settings)
    assert large_maze.has_42 is True


def test_easter_egg_activation() -> None:
    """Test that easter eggs are activated on large grids (>= 90x30)."""
    large_settings: dict[str, Any] = {
        "WIDTH": 100,
        "HEIGHT": 40,
        "ENTRY": (0, 0),
        "EXIT": (99, 39),
        "PERFECT": True,
    }
    maze = Maze(large_settings)

    # Verificamos que se han estampado los nombres
    assert maze.easter_egg is True


def test_easter_egg_inactive_on_normal_grids(
    default_settings: dict[str, object]
) -> None:
    """Test that easter egg is not activated on standard size grids."""
    maze = Maze(default_settings)
    assert getattr(maze, "easter_egg", False) is False
