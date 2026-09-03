"""Unit tests for configuration parsing and validation functions."""

import pytest
import configuration


def test_parse_config_valid(tmp_path: pytest.TempPathFactory) -> None:
    """Test parsing a valid configuration file."""
    config_file = tmp_path / "config.txt"  # type: ignore[operator]
    config_file.write_text(
        "WIDTH=10\n"
        "HEIGHT=10\n"
        "ENTRY=0,0\n"
        "EXIT=9,9\n"
        "OUTPUT_FILE=out.txt\n"
        "PERFECT=True\n"
        "SEED=42\n"
    )

    config = configuration.parse_config(str(config_file))
    assert config["WIDTH"] == 10
    assert config["HEIGHT"] == 10
    assert config["ENTRY"] == (0, 0)
    assert config["EXIT"] == (9, 9)
    assert config["OUTPUT_FILE"] == "out.txt"
    assert config["PERFECT"] is True
    assert config["SEED"] == 42


def test_parse_config_syntax_error(
    tmp_path: pytest.TempPathFactory
) -> None:
    """Test parsing a line missing an equal sign."""
    config_file = tmp_path / "invalid_syntax.txt"  # type: ignore[operator]
    config_file.write_text("INVALID_LINE_WITHOUT_EQUALS\n")

    with pytest.raises(ValueError, match="Expected 'KEY=VALUE'"):
        configuration.parse_config(str(config_file))


def test_parse_config_duplicate_key(
    tmp_path: pytest.TempPathFactory
) -> None:
    """Test parsing duplicate keys."""
    config_file = tmp_path / "duplicate.txt"  # type: ignore[operator]
    config_file.write_text("WIDTH=10\nWIDTH=20\n")

    with pytest.raises(ValueError, match="Duplicate key found"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_int(
    tmp_path: pytest.TempPathFactory
) -> None:
    """Test parsing an invalid integer value."""
    config_file = tmp_path / "invalid_int.txt"  # type: ignore[operator]
    config_file.write_text("WIDTH=ten\n")

    with pytest.raises(ValueError, match="Invalid value for WIDTH"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_coords(
    tmp_path: pytest.TempPathFactory
) -> None:
    """Test parsing invalid coordinate formatting."""
    config_file = tmp_path / "invalid_coords.txt"  # type: ignore[operator]
    config_file.write_text("ENTRY=0\n")

    with pytest.raises(ValueError, match="Invalid coordinates for ENTRY"):
        configuration.parse_config(str(config_file))


def test_parse_config_invalid_boolean(
    tmp_path: pytest.TempPathFactory
) -> None:
    """Test parsing an invalid boolean value."""
    config_file = tmp_path / "invalid_bool.txt"  # type: ignore[operator]
    config_file.write_text("PERFECT=Maybe\n")

    with pytest.raises(ValueError, match="expected 'True' or 'False'"):
        configuration.parse_config(str(config_file))


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
