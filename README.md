*This project has been created as part of the 42 curriculum by <jruiz-ag & rumartin>*  <!-- markdownlint-disable-line -->

# A-Maze-ing

## Description

A-Maze-ing is a robust and modular maze generator built in Python 3.10+. It is capable of generating both "perfect" mazes (a single valid path between two points) and "imperfect" playable boards (Pac-Man style with multiple loops and minimized dead-ends). The project features a custom bitwise matrix for optimized storage, a Breadth-First Search (BFS) pathfinding solver, real-time terminal rendering, and a fully decoupled architecture meant to be packaged and reused in future applications.

## Instructions

The project requires Python 3.10 or higher. All dependencies, linting, and testing are managed via the included `Makefile`.

### Installation & Execution

1. **Setup the virtual environment and install tools:**

```bash
make install
```

2. **Run the program:** <!-- markdownlint-disable-line -->

```bash
make run
# Which executes: python3 a_maze_ing.py config.txt
```

You can also run it manually passing a custom configuration file:

```python
source .venv/bin/activate
python3 a_maze_ing.py my_custom_config.txt
```

### Development & Testing

Run Linter (Flake8 & Mypy): make lint or make lint-strict
Run Unit Tests (Pytest): make test
Clean Cache & Build Files: make clean
Full Cleanup (breaks venv): make fclean

### Configuration file format

The program reads a plain text configuration file using a strict KEY=VALUE format. Empty lines and lines starting with # are ignored.

| Key                      | Type    | Description                                                           | Example                |
|--------------------------|---------|-----------------------------------------------------------------------|------------------------|
| `WIDTH`                  | Integer | Maze width in cells (min 4).                                          | `WIDTH=20`             |
| `HEIGHT`                 | Integer | Maze height in cells (min 4).                                         | `HEIGHT=15`            |
| `ENTRY`                  | X, Y    | Starting coordinates.                                                 | `ENTRY=0,0`            |
| `EXIT`                   | X, Y    | Target coordinates.                                                   | `EXIT=19,14`           |
| `OUTPUT_FILE`            | String  | Name of the exported hex text file.                                   | `OUTPUT_FILE=maze.txt` |
| `PERFECT`                | Boolean | `True` for a single-path maze, `False` for Pac-Man mode.              | `PERFECT=True`         |
| `SEED` *(Optional)*      | Integer | Ensures deterministic procedural generation.                          | `SEED=42`              |
| `GAME_MODE` *(Optional)* | String  | Dead-end removal (`Bonus`, `Easy`, `Medium`, `Hard`, `Insane`).       | `GAME_MODE=Easy`       |
| `DELAY` *(Optional)*     | Float   | Delay in seconds for live terminal rendering.                         | `DELAY=0.05`           |

### Maze Generation Algorithm

We implemented Wilson's Algorithm for the core maze generation.

#### Why Wilson's?

Many standard maze algorithms (like Recursive Backtracker or Prim's) introduce noticeable structural biases—such as excessively long straight corridors or a heavily radial layout. Wilson's algorithm generates an unbiased uniform spanning tree using loop-erased random walks. This means every possible perfect maze has an equal probability of being generated, resulting in highly unpredictable, complex, and aesthetically pleasing structures.

### Advanced Features

Pac-Man Mode: When PERFECT=False, a post-processing algorithm traverses the perfect maze to tear down walls, open the four corners, and strategically break dead-ends based on the GAME_MODE parameter, creating multiple independent routes.

Embedded Templates: The generator intelligently stamps a "42" shape in the center of the maze and includes hidden easter eggs for the developers if the dimensions allow it.

### Code Reusability (mazegen)

The generation logic has been strictly decoupled from the CLI interface into a facade class called MazeGenerator. This module is designed to be distributed via pip (e.g., mazegen-1.0.0-py3-none-any.whl).

How to reuse it:

```python
from mazegen import MazeGenerator

# 1. Initialize with settings
settings = {
    "WIDTH": 20, "HEIGHT": 20, "ENTRY": (0, 0), "EXIT": (19, 19),
    "PERFECT": True, "SEED": 12345
}
generator = MazeGenerator(settings)

# 2. Generate the maze object
maze = generator.generate()

# 3. Solve the maze and get the path (e.g., "NNEESSW")
solution = generator.solve()

# 4. Export to the 42 subject format
generator.export("my_maze_data.txt")
```

Note: Refer to LICENSE.md (MIT) for redistribution rights.

### Team and Project Management

Jaime & Ruben: We adopted a pair-programming approach for the core algorithmic challenges (Bitwise logic, Wilson's implementation, and BFS solver) to ensure both members fully understood the mathematical operations.  

Roles: Work was split dynamically. One focused on the parser, configuration validation, and unit testing (pytest suite), while the other developed the rendering engine and exporter.

Planning: We initially underestimated the complexity of the "Pac-Man" mode (removing dead-ends while maintaining valid states), which required us to refactor our wall-breaking logic mid-project.

What worked well: Using bit masks (1, 2, 4, 8) to represent walls saved enormous amounts of memory and simplified the hex exporting process. Setting up the Makefile and pytest early caught numerous regressions.  Tools used: Git, GitHub, Python venv, Flake8, Mypy, Pytest.

### Resources & AI Usage

Graph Theory & Algorithms: Wikipedia articles on Maze generation algorithms (specifically Wilson's) and Breadth-first search.

AI Tools (LLMs): AI was used strictly as a thought partner and code-reviewer to adhere to the 42 AI guidelines. Specifically, it was used to:

1. Generate edge-case ideas for the pytest suite.

2. Review and optimize the regex patterns in our parsing module.

3. Audit our final codebase for PEP8/Flake8 compliance and catch missing English translations in our docstrings. No direct code was copy-pasted without a full understanding and peer-review process.
