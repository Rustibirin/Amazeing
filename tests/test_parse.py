"""Unit tests for configuration parsing and Pydantic validation."""

from pathlib import Path
import pytest
from pydantic import ValidationError
import parser as config_parser
from generator import MazeGenerator


def test_parse_config_valid(tmp_path: Path) -> None:
    """Test parsing a valid configuration file."""
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "WIDTH=10\n"
        "HEIGHT=10\n"
        "ENTRY=0,0\n"
        "EXIT=9,9\n"
        "OUTPUT_FILE=out.txt\n"
        "PERFECT=True\n"
        "SEED=42\n",
        encoding="utf-8",
    )

    config = config_parser.parse_config(str(config_file))
    assert config["WIDTH"] == 10
    assert config["HEIGHT"] == 10
    assert config["ENTRY"] == (0, 0)
    assert config["EXIT"] == (9, 9)
    assert config["OUTPUT_FILE"] == "out.txt"
    assert config["PERFECT"] is True
    assert config["SEED"] == 42


def test_parse_config_syntax_error(tmp_path: Path) -> None:
    """Test parsing a line missing an equal sign."""
    config_file = tmp_path / "invalid_syntax.txt"
    config_file.write_text("INVALID_LINE_WITHOUT_EQUALS\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        config_parser.parse_config(str(config_file))


def test_parse_config_invalid_int(tmp_path: Path) -> None:
    """Test parsing an invalid integer value."""
    config_file = tmp_path / "invalid_int.txt"
    config_file.write_text("WIDTH=ten\n", encoding="utf-8")

    # El parser básico devolverá el string 'ten'
    config = config_parser.parse_config(str(config_file))
    assert config["WIDTH"] == "ten"


# --- Tests de validación delegados a Pydantic en MazeGenerator ---

def test_validate_config_missing_key() -> None:
    """Test validation when a required key is missing."""
    missing_key_config = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        # Falta PERFECT
    }
    with pytest.raises(ValidationError):
        MazeGenerator(settings=missing_key_config)


def test_validate_config_small_dimensions() -> None:
    """Test validation when dimensions are smaller than or equal to 3."""
    small_config = {
        "WIDTH": 3,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (2, 2),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
    }
    with pytest.raises(ValidationError, match="must be at least 4"):
        MazeGenerator(settings=small_config)


def test_validate_config_entry_out_of_bounds() -> None:
    """Test validation when entry coordinates are out of bounds."""
    bad_entry = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (15, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
    }
    with pytest.raises(ValidationError, match="is out of bounds"):
        MazeGenerator(settings=bad_entry)


def test_validate_config_same_entry_exit() -> None:
    """Test validation when entry and exit are in the same location."""
    same_cell = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (5, 5),
        "EXIT": (5, 5),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
    }
    with pytest.raises(ValidationError, match="must be different"):
        MazeGenerator(settings=same_cell)


def test_validate_config_invalid_algorithm() -> None:
    """Test validation when ALGORITHM is provided but not supported."""
    invalid_algo = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
        "ALGORITHM": "astar",  # Algoritmo inválido
    }
    with pytest.raises(ValidationError, match="must be 'WILSON' or 'DFS'"):
        MazeGenerator(settings=invalid_algo)


def test_validate_config_invalid_algorithm_type() -> None:
    """Test validation when ALGORITHM is not a string."""
    invalid_algo_type = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
        "ALGORITHM": 42,  # Debe ser un string
    }
    with pytest.raises(ValidationError, match="must be a string"):
        MazeGenerator(settings=invalid_algo_type)


def test_validate_config_valid_algorithm_uppercase() -> None:
    """Test validation normalizes uppercase algorithms correctly."""
    valid_algo = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
        "ALGORITHM": "DFS",  # Mayúsculas, debería normalizarse
    }
    generator = MazeGenerator(settings=valid_algo)
    assert generator.settings["ALGORITHM"] == "DFS"


def test_validate_config_invalid_difficulty() -> None:
    """Test validation when DIFFICULTY is provided but invalid."""
    invalid_difficulty = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
        "DIFFICULTY": "impossible",  # Dificultad no soportada
    }
    with pytest.raises(ValidationError, match="Must be one of"):
        MazeGenerator(settings=invalid_difficulty)
