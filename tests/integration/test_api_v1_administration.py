import json

import pytest
from core import config
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_import_rates(async_client: AsyncClient) -> None:
    rates_json = {
        "2024-11-30": [
            {"cargo_type": "Glass", "rate": "0.015"},
            {"cargo_type": "Other", "rate": "0.04"},
        ],
        "2024-12-01": [
            {"cargo_type": "Glass", "rate": "0.01"},
            {"cargo_type": "Other", "rate": "0.05"},
        ],
    }
    rate_to_check: dict[str, float | str] = {
        "date": "2024-11-30",
        "cargo_type": "Glass",
        "rate": 0.015,
    }
    rates_file = config.BASE_DIR.parent / "data" / "import_rates.json"
    rates_file.write_text(json.dumps(rates_json), encoding="utf-8")

    response = await async_client.get(url="/v1/administration/import_rates/")
    assert response.status_code == 204

    check_response = await async_client.get(
        url="/v1/rates/", params={"date": rate_to_check["date"]}
    )
    assert check_response.status_code == 200

    sought_rate_list = [
        rate
        for rate in check_response.json()
        if rate["cargo_type"] == rate_to_check["cargo_type"]
    ]
    assert len(sought_rate_list) == 1
    sought_rate = sought_rate_list[0]
    assert sought_rate.get("id") is not None
    assert sought_rate["cargo_type"] == rate_to_check["cargo_type"]
    assert sought_rate.get("date") == rate_to_check["date"]
    assert sought_rate.get("rate") == rate_to_check["rate"]
