import pytest
from persona import load_personas


def test_load_personas_returns_dict():
    personas = load_personas("personas.json")
    assert isinstance(personas, dict)
    assert "Expert" in personas


def test_load_personas_missing_file(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        load_personas(str(missing))
