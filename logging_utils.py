import json
import datetime
from typing import Any, Dict, List


def time_str() -> str:
    """Return the current UTC time as a string."""
    return str(datetime.datetime.utcnow())


def json_log(f_name: str, key: str, data: Any) -> None:
    """Append data under key in a JSON file."""
    with open(f_name, "r", encoding="utf-8") as jsonFile:
        old_data = json.load(jsonFile)
    old_data.setdefault(key, []).append(data)
    with open(f_name, "w", encoding="utf-8") as jsonFile:
        json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)


def session_log(log_file: str, context: List[Dict[str, str]], init_time: str, model: str) -> None:
    """Append a session entry to the log file."""
    log_content = {
        "start": init_time,
        "end": time_str(),
        "model": model,
        "content": context,
    }
    json_log(log_file, "chats", log_content)
