"""Unit tests for the Solver module and BFS pathfinding algorithm."""

import pytest
from maze import Maze
from solver import Solver


@pytest.fixture
def small_maze_settings() -> dict[str, object]:
    """Returns basic settings for a 3x3 grid."""
    return {
        "WIDTH": 3,
        "HEIGHT": 3,
        "ENTRY": (0, 0),
        "EXIT": (2, 0),
        "PERFECT": True,
    }


def test_solver_simple_straight_path(
    small_maze_settings: dict[str, object]
) -> None:
    """Test solver on a simple horizontal corridor."""
    maze = Maze(small_maze_settings)
    solver = Solver()

    maze.break_wall(0, 0, Maze.EAST, Maze.WEST, 1, 0)
    maze.break_wall(1, 0, Maze.EAST, Maze.WEST, 2, 0)

    solution = solver.solve(maze)
    assert solution == "EE"


def test_solver_unreachable_exit(
    small_maze_settings: dict[str, object]
) -> None:
    """Test solver raises ValueError when exit is completely isolated."""
    maze = Maze(small_maze_settings)
    solver = Solver()

    with pytest.raises(
        ValueError, match="No valid path found between ENTRY and EXIT."
    ):
        solver.solve(maze)


def test_solver_resets_visited_flags_on_success(
    small_maze_settings: dict[str, object]
) -> None:
    """Test that VISITED bits are cleared after finding a path."""
    maze = Maze(small_maze_settings)
    solver = Solver()

    maze.break_wall(0, 0, Maze.EAST, Maze.WEST, 1, 0)
    maze.break_wall(1, 0, Maze.EAST, Maze.WEST, 2, 0)

    solver.solve(maze)

    for y in range(maze.height):
        for x in range(maze.width):
            assert maze.is_visited(x, y) is False


def test_solver_resets_visited_flags_on_failure(
    small_maze_settings: dict[str, object]
) -> None:
    """Test that VISITED bits are cleared even when pathfinding fails."""
    maze = Maze(small_maze_settings)
    solver = Solver()

    with pytest.raises(ValueError):
        solver.solve(maze)

    for y in range(maze.height):
        for x in range(maze.width):
            assert maze.is_visited(x, y) is False


def test_solver_ignores_solid_cells(
    small_maze_settings: dict[str, object]
) -> None:
    """Test that solver avoids cells marked as SOLID."""
    maze = Maze(small_maze_settings)
    solver = Solver()

    maze.break_wall(0, 0, Maze.SOUTH, Maze.NORTH, 0, 1)
    maze.mark_solid(0, 1)

    with pytest.raises(ValueError):
        solver.solve(maze)


def test_solver_same_entry_and_exit() -> None:
    """Test edge case where entry and exit are the exact same cell."""
    settings: dict[str, object] = {
        "WIDTH": 4,
        "HEIGHT": 4,
        "ENTRY": (1, 1),
        "EXIT": (1, 1),
        "PERFECT": True,
    }
    maze = Maze(settings)
    solver = Solver()

    solution = solver.solve(maze)
    assert solution == ""
