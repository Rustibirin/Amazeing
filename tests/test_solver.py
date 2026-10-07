"""Unit tests for the Solver module and BFS pathfinding algorithm."""

import pytest
from maze import Maze
from solver import Solver
from typing import Any


@pytest.fixture
def small_maze_settings() -> dict[str, Any]:
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


def test_solver_path_validity_step_by_step(
    small_maze_settings: dict[str, object]
) -> None:
    """
    Test that the solution path physically
    connects entry to exit without crossing walls.
    """

    maze = Maze(small_maze_settings)
    maze.break_wall(0, 0, Maze.EAST, Maze.WEST, 1, 0)
    maze.break_wall(1, 0, Maze.EAST, Maze.WEST, 2, 0)

    solver = Solver()
    path = solver.solve(maze)

    curr_x, curr_y = maze.entry
    dir_map = {
        'N': (0, -1, Maze.NORTH),
        'S': (0, 1, Maze.SOUTH),
        'E': (1, 0, Maze.EAST),
        'W': (-1, 0, Maze.WEST),
    }

    for step in path:
        dx, dy, wall_flag = dir_map[step]
        assert maze.has_wall(curr_x, curr_y, wall_flag) is False
        curr_x += dx
        curr_y += dy

    assert (curr_x, curr_y) == maze.exit
