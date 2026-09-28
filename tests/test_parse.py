"""Unit tests for configuration parsing and validation functions."""

from pathlib import Path
import pytest
import configuration  # type: ignore[import-not-found]


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

    config = configuration.parse_config(str(config_file))
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

    with pytest.raises(ValueError, match="Expected 'KEY=VALUE'"):
        configuration.parse_config(str(config_file))


def test_parse_config_duplicate_key(tmp_path: Path) -> None:
    """Test parsing duplicate keys."""
    config_file = tmp_path / "duplicate.txt"
    config_file.write_text("WIDTH=10\nWIDTH=20\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate key found"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_int(tmp_path: Path) -> None:
    """Test parsing an invalid integer value."""
    config_file = tmp_path / "invalid_int.txt"
    config_file.write_text("WIDTH=ten\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid value for WIDTH"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_coords(tmp_path: Path) -> None:
    """Test parsing invalid coordinate formatting."""
    config_file = tmp_path / "invalid_coords.txt"
    config_file.write_text("ENTRY=0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid coordinates for ENTRY"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_boolean(tmp_path: Path) -> None:
    """Test parsing an invalid boolean value."""
    config_file = tmp_path / "invalid_bool.txt"
    config_file.write_text("PERFECT=Maybe\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected 'True' or 'False'"):
        configuration.parse_config(str(config_file))


def test_parse_config_game_mode_and_delay(tmp_path: Path) -> None:
    """Test parsing valid GAME_MODE and DELAY settings."""
    config_file = tmp_path / "optional.txt"
    config_file.write_text("GAME_MODE=easy\nDELAY=0.05\n", encoding="utf-8")

    config = configuration.parse_config(str(config_file))
    assert config["GAME_MODE"] == 0.8
    assert config["DELAY"] == 0.05


def test_parse_config_invalid_game_mode(tmp_path: Path) -> None:
    """Test parsing an invalid GAME_MODE string."""
    config_file = tmp_path / "bad_mode.txt"
    config_file.write_text("GAME_MODE=nightmare\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected 'Easy', 'Medium'"):
        configuration.parse_config(str(config_file))


def test_parse_config_negative_delay(tmp_path: Path) -> None:
    """Test parsing a negative DELAY value."""
    config_file = tmp_path / "bad_delay.txt"
    config_file.write_text("DELAY=-0.5\n", encoding="utf-8")

    with pytest.raises(ValueError, match="cannot be negative"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_output_file(tmp_path: Path) -> None:
    """Test parsing OUTPUT_FILE with invalid path characters."""
    config_file = tmp_path / "bad_output.txt"
    config_file.write_text("OUTPUT_FILE=invalid/path.txt\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid character"):
        configuration.parse_config(str(config_file))


def test_parse_config_comments_and_blank_lines(tmp_path: Path) -> None:
    """Test that comments and empty lines are correctly ignored."""
    config_file = tmp_path / "comments.txt"
    config_file.write_text(
        "# This is a comment\n"
        "\n"
        "WIDTH=10\n"
        "  # Another comment  \n"
        "HEIGHT=10\n",
        encoding="utf-8",
    )

    config = configuration.parse_config(str(config_file))
    assert config["WIDTH"] == 10
    assert config["HEIGHT"] == 10


def test_validate_config_valid() -> None:
    """Test validation with valid dictionary settings."""
    valid_config = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
    }
    configuration.validate_config(valid_config)


def test_validate_config_missing_key() -> None:
    """Test validation when a required key is missing."""
    missing_key_config = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 9),
        "OUTPUT_FILE": "out.txt",
    }
    with pytest.raises(ValueError, match="missing: PERFECT"):
        configuration.validate_config(missing_key_config)


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
    with pytest.raises(ValueError, match="must be greater than 3"):
        configuration.validate_config(small_config)


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
    with pytest.raises(ValueError, match="outside the maze boundaries"):
        configuration.validate_config(bad_entry)


def test_validate_config_exit_out_of_bounds() -> None:
    """Test validation when exit coordinates are out of bounds."""
    bad_exit = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (0, 0),
        "EXIT": (9, 15),
        "OUTPUT_FILE": "out.txt",
        "PERFECT": True,
    }
    with pytest.raises(ValueError, match="outside the maze boundaries"):
        configuration.validate_config(bad_exit)


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
    with pytest.raises(ValueError, match="cannot be in the same cell"):
        configuration.validate_config(same_cell)
