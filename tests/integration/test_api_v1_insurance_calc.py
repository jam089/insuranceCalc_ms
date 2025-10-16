from random import randint

import pytest
from api.v1.schemas import CalcRequest
from db.models import Rate
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_insurance_calculation(
    async_client: AsyncClient,
    test_rates: Rate,
) -> None:
    request = CalcRequest(
        user_id=randint(1, 99),
        declared_value=randint(100, 9000),
        cargo_type=test_rates.cargo_type,
        date=test_rates.date,
    )
    response = await async_client.get(
        url="/v1/insurance_calculation/", params=request.model_dump()
    )
    assert response.status_code == 200

    assert response.json().get("request") == request.model_dump(mode="json")
    assert response.json().get("insurance_value") is not None
    expected_insurance_value = round(test_rates.rate * request.declared_value, 2)
    assert response.json().get("insurance_value") == expected_insurance_value
