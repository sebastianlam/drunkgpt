import json
from typing import Dict


def load_personas(path: str) -> Dict[str, str]:
    """Load persona definitions from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Persona file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Persona file is not valid JSON: {path}") from e


def persona_display(personas: Dict[str, str]) -> Dict[int, str]:
    """Return a mapping of numeric options to persona names."""
    return dict(enumerate(personas.keys(), 1))
