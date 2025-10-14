import json
from pathlib import Path


def json_read(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {**data}
