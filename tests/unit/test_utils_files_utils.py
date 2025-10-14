import json
from pathlib import Path

import pytest
from utils.files_utils import json_read

pytestmark = pytest.mark.unit


test_json = {
    "parents": [
        {
            "name": "Homer",
            "surname": "Simpson",
            "age": "34",
        },
        {
            "name": "Marge",
            "surname": "Simpson",
            "age": "39",
        },
    ],
    "kids": [
        {
            "name": "Lisa",
            "surname": "Simpson",
            "age": "8",
        },
        {
            "name": "Bart",
            "surname": "Simpson",
            "age": "10",
        },
    ],
}


@pytest.mark.asyncio
async def test_json_read(tmp_path: Path) -> None:
    file_path = tmp_path / "data.json"
    file_path.write_text(json.dumps(test_json), encoding="utf-8")

    response = json_read(file_path)

    assert isinstance(response, dict)
    assert test_json == response
