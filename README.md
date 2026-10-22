*This project has been created as part of the 42 curriculum by jruiz-ag & rumartin*  <!-- markdownlint-disable-line -->

# A-MAZE-ING - @42Malaga <img align="right" src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python" alt="Language Python"> <!-- markdownlint-disable MD033 -->

## Description

This project is a feature-complete, highly modular maze generator and interactive terminal application built in Python 3.10+. It supports multiple generation algorithms to create both "perfect" mazes (a single unique path between entry and exit) and "imperfect" Pac-Man style boards featuring customizable difficulty levels.

Beyond procedural generation, the project offers an **interactive Play Mode** that allows users to manually navigate and solve the maze directly in the terminal using standard WASD controls. Powered by a custom bitwise matrix for memory-efficient cell representation, A-Maze-ing includes automated Breadth-First Search (BFS) pathfinding, real-time generation animations, dynamic color customization, and embedded custom visual patterns ("42"). The core generation logic is strictly decoupled as a standalone reusable library (`mazegen`), fully prepared for pip packaging and distribution.

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

```bash
source .venv/bin/activate
python3 a_maze_ing.py custom_config.txt
```

### Development & Testing

1. **Clean build files** <!-- markdownlint-disable-line -->

To remove temporary files:

```bash
make clean
# Or perform a complete cleanup:
make fclean
```

2. **Test and Lint**  <!-- markdownlint-disable-line -->

```bash
make test
```

```bash
make lint
# Or strict static analysis:
make lint-strict
```

### Configuration file format

The program reads a plain text configuration file using a strict KEY=VALUE format. Empty lines and lines starting with # are ignored.

| Key                       | Type    | Description                                                           | Example                |
|---------------------------|---------|-----------------------------------------------------------------------|------------------------|
| `WIDTH`                   | Integer | Maze width in cells (min 4).                                          | `WIDTH=20`             |
| `HEIGHT`                  | Integer | Maze height in cells (min 4).                                         | `HEIGHT=15`            |
| `ENTRY`                   | X, Y    | Starting coordinates.                                                 | `ENTRY=0,0`            |
| `EXIT`                    | X, Y    | Target coordinates.                                                   | `EXIT=19,14`           |
| `OUTPUT_FILE`             | String  | Name of the exported hex text file.                                   | `OUTPUT_FILE=maze.txt` |
| `PERFECT`                 | Boolean | `True` for a single-path maze, `False` for Pac-Man mode.              | `PERFECT=True`         |
| `SEED` *(Optional)*       | Integer | Ensures deterministic procedural generation.                          | `SEED=42`              |
| `DIFFICULTY` *(Optional)* | String  | Dead-end removal (`Bonus`, `Easy`, `Medium`, `Hard`, `Insane`).       | `DIFFICULTY=Easy`      |
| `DELAY` *(Optional)*      | Float   | Delay in seconds for live terminal rendering.                         | `DELAY=0.05`           |
| `ALGORITHM` *(Optional)*  | String  | Generation algorithm (`Wilson`, `DFS`).                               | `ALGORITHM=Wilson`     |

### Maze Generation Algorithms

We decided to implement and evaluate multiple graph-based procedural generation techniques to offer distinct maze structural behaviors:

1. **Wilson's Algorithm (Default):**

Mechanism: Uses uniform loop-erased random walks to build a spanning tree.

Why chosen: Standard algorithms like Recursive Backtracker or Prim's introduce structural biases (e.g., long straight corridors or radial patterns). Wilson's algorithm produces an unbiased uniform distribution over all possible spanning trees, resulting in highly unpredictable, complex, and aesthetically pleasing structures.

2. **Depth-First Search Algorithm:** <!-- markdownlint-disable-line -->

Mechanism: Traverses the grid deeply before backtracking, carving paths until dead ends are reached.

Why chosen: Produces mazes with longer, windier paths and fewer short dead-ends compared to Wilson's, offering a noticeably different aesthetic and difficulty profile.

### Advanced Features

Beyond the mandatory specifications, A-Maze-ing incorporates several advanced features, official project bonuses, and terminal UX enhancements:

* **Interactive WASD Play Mode:** An interactive terminal game mode allowing players to manually walk through and solve the generated maze cell-by-cell using `W`, `A`, `S`, `D` keys with real-time TUI updates.

* **Pac-Man Mode & Custom Difficulty Scaling:** When `PERFECT=False`, a post-processing algorithm opens all four corners/center and breaks dead-ends to guarantee multiple independent routes. Includes a dynamic `DIFFICULTY` system (`Easy` through `Insane`), featuring a special `Bonus` level that produces a fully `braided maze` (0 dead-ends).

* **Multi-Algorithm Engine:** Full support for both **Wilson's Algorithm** (unbiased uniform spanning trees) and **Depth-First Search (DFS)**, allowing users to compare different maze generation behaviors.

* **Real-Time Generation Animation:** Live terminal visualization of the maze generation process step-by-step with customizable frame `delays`.

* **Dynamic Interactive TUI Dashboard:** A live menu interface to adjust generation settings on the fly without restarting the program (toggle algorithms, switch between Perfect/Pac-Man modes, tune difficulty, rotate color palettes, toggle animations, or reload `config.txt`).

* **Embedded Templates & Easter Egg:** Intelligent center-stamping logic for the "42" pattern with bounds checking, along with a hidden embedded visual `easter egg`.

### Code Reusability (mazegen)

The maze generation logic is completely decoupled from the CLI interface inside the `MazeGenerator` class. It can be built and distributed as a standalone wheel package `(mazegen-1.0.0-py3-none-any.whl)`.

How to reuse it:

```python

from mazegen import MazeGenerator

# 1. Configuration parameters
settings = {
    "WIDTH": 15,
    "HEIGHT": 10,
    "ENTRY": (0, 0),
    "EXIT": (14, 9),
    "PERFECT": True,
    "OUTPUT_FILE": "test_maze.txt",
    "SEED": 12345,
    "ALGORITHM": "WILSON"
}

# 2. Initiate and generate the maze
generator = MazeGenerator(settings=settings)
print("MazeGenerator successfully initialized!")
maze, _ = generator.generate()
print(f"Maze of {maze.width}x{maze.height} successfully generated!")

# 3. Find solution
solution = generator.solve()
print(f"Solution found! Steps: {solution}")

# 4. Export to hexadecimal file format
generator.export()
print(f"Maze successfully exported to {settings['OUTPUT_FILE']}!")
```

Note: Refer to LICENSE.md (MIT) for redistribution rights.

## Team and Project Management

`A-Maze-ing` was designed as a collaborative project, combining pair programming for key algorithmic challenges with specialized task distribution:

|   User   |                                        Files & Modules                                    |
|----------|-------------------------------------------------------------------------------------------|
| jruiz-ag | mazegen/ (parser.py, builder.py, generator.py), tests/, Makefile, pyproject.toml         |
| rumartin | a_maze_ing.py, mazegen/ (maze.py, solver.py, exporter.py, templates.py), ui/, assets/    |

### Roles & Dynamics

`jruiz-ag:` Focused on strict configuration parsing, Pydantic validations, pytest unit testing suite, and Python packaging configuration (setuptools/build)

`rumartin:` Developed the bitwise matrix data structure, Wilson & DFS algorithms, BFS solver, interactive TUI menu, and ASCII visualizer.

`Pair Programming:` Jointly tackled bitwise mask operations and dead-end removal logic for Pac-Man mode.

#### Planning evolution

Initial Plan: Build a simple generator and CLI interface.

Evolution: Mid-project, the complexity of opening loops for Pac-Man mode required refactoring wall-breaking methods to ensure shared walls between neighboring cells were updated atomically.

#### What Worked Well

Bitwise flags (1, 2, 4, 8) saved memory and simplified hexadecimal exporting.

Setting up Makefile, flake8, mypy, and pytest early caught regressions instantly.

#### What Could Be Improved

TUI menu loop could be further refactored into smaller sub-modules.

Automated terminal interaction testing could be expanded using terminal mocking.

#### Tools Used

Git, GitHub, Python venv, pip, flake8, mypy, pytest, Pydantic.

## Resources

**Graph Theory & Maze Algorithms:** Wikipedia articles on Maze generation algorithms (Wilson's Uniform Spanning Trees, DFS) and Breadth-First Search (BFS).

**Python Packaging:** Official Python Packaging User Guide (build, setuptools).

**Peer-to-Peer Learning:** Collaborative discussions with 42 peers regarding different points of view to structure and build the project.

**AI usage:** AI was used strictly as a thought partner, code auditor, and learning assistant in full compliance with the 42 AI usage guidelines. To ensure effective interactions, structured **prompt engineering techniques** (such as role prompting, iterative refinement, and system constraint definitions) were applied to evaluate and validate output quality. Specifically, it was used to:

1. Generate edge-case ideas for the pytest suite.

2. Audit our final codebase for PEP8/Flake8 compliance and catch missing English translations in our docstrings.

3. Formulate detailed, context-aware prompts to review architecture design options and debug complex algorithmic edge cases.

*Note: No direct code was copy-pasted without a full understanding and peer-review process.*
