"""mazegen - Reusable Maze Generator Module for 42 A-Maze-ing."""

from mazegen.generator import MazeGenerator
from mazegen.maze import Maze
from mazegen.parser import GameMode, parse_config

__all__ = ["MazeGenerator", "Maze", "GameMode", "parse_config"]

