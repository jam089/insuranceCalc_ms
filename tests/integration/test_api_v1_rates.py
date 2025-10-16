from datetime import date

import pytest
from db.models import Rate
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_rate_by_id(
    async_client: AsyncClient,
    test_rates: Rate,
) -> None:
    response = await async_client.get(url=f"/v1/rates/{test_rates.id}/")

    assert response.status_code == 200
    assert response.json().get("id") == test_rates.id
    assert date.fromisoformat(response.json().get("date")) == test_rates.date
    assert response.json().get("cargo_type") == test_rates.cargo_type
    assert response.json().get("rate") == test_rates.rate


@pytest.mark.asyncio
async def test_get_rate_by_date(
    async_client: AsyncClient,
    test_rates: Rate,
) -> None:
    response = await async_client.get(
        url="/v1/rates/", params={"date": test_rates.date.strftime("%Y-%m-%d")}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    exist_in_response = False
    for rate in response.json():
        if rate["id"] == test_rates.id:
            exist_in_response = True
            break
    assert exist_in_response


@pytest.mark.asyncio
async def test_create_rate(
    async_client: AsyncClient,
) -> None:
    create_json = {
        "date": "2001-04-02",
        "cargo_type": "Glass",
        "rate": 0.002,
    }

    response = await async_client.post(
        url="/v1/rates/",
        json=create_json,
    )

    assert response.status_code == 201
    assert response.json().get("id") is not None
    assert response.json().get("date") == create_json["date"]
    assert response.json().get("cargo_type") == create_json["cargo_type"]
    assert response.json().get("rate") == create_json["rate"]


@pytest.mark.asyncio
async def test_update_rate_replace(
    async_client: AsyncClient,
    test_rates: Rate,
) -> None:
    update_json = {
        "date": "2001-04-02",
        "cargo_type": "Glass",
        "rate": 0.002,
    }
    response = await async_client.put(
        url=f"/v1/rates/{test_rates.id}/",
        json=update_json,
    )

    assert response.status_code == 200
    assert response.json().get("id") == test_rates.id
    assert response.json().get("date") == update_json["date"]
    assert response.json().get("cargo_type") == update_json["cargo_type"]
    assert response.json().get("rate") == update_json["rate"]


@pytest.mark.asyncio
async def test_update_rate_add_new(
    async_client: AsyncClient,
) -> None:
    update_json = {
        "date": "2001-04-02",
        "cargo_type": "Glass",
        "rate": 0.002,
    }
    response = await async_client.put(
        url=f"/v1/rates/{999}/",
        json=update_json,
    )

    assert response.status_code == 201
    assert response.json().get("id") is not None
    assert response.json().get("date") == update_json["date"]
    assert response.json().get("cargo_type") == update_json["cargo_type"]
    assert response.json().get("rate") == update_json["rate"]


@pytest.mark.parametrize(
    "update_json",
    [
        {
            "date": "2001-04-02",
            "cargo_type": "Glass",
            "rate": 0.002,
        },
        {
            "rate": 0.007,
        },
        {
            "date": "2021-04-02",
        },
        {
            "cargo_type": "Beer",
        },
        {
            "date": "1998-04-02",
            "rate": 0.2,
        },
    ],
)
@pytest.mark.asyncio
async def test_update_rate_partial(
    async_client: AsyncClient,
    test_rate_a: Rate,
    update_json: dict,
) -> None:
    response = await async_client.patch(
        url=f"/v1/rates/{test_rate_a.id}/",
        json=update_json,
    )

    assert response.status_code == 200
    assert response.json().get("id") == test_rate_a.id
    for key, value in update_json.items():
        assert response.json().get(key) == value


@pytest.mark.asyncio
async def test_delete_rate(
    async_client: AsyncClient,
    test_rates: Rate,
) -> None:
    delete_id = test_rates.id
    response = await async_client.delete(
        url=f"/v1/rates/{delete_id}/",
    )
    assert response.status_code == 204

    chack_response = await async_client.get(
        url=f"/v1/rates/{delete_id}/",
    )
    assert chack_response.status_code == 404
