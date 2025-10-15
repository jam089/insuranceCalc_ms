from datetime import date

import pytest
from api.v1.routes.insurance_calc import insurance_calculation
from api.v1.schemas.insurance_calc import CalcRequest
from db.models import Rate
from fastapi.exceptions import HTTPException
from pytest_mock import MockFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_rate(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    rate = Rate(rate=0.03, cargo_type="Glass", date=date.fromisoformat("2020-11-03"))
    mocker.patch(
        "api.v1.routes.insurance_calc.get_insurance_rate_for_calc",
        new_callable=mocker.AsyncMock,
        return_value=rate,
    )
    declared_value = 3000
    request_json = {
        "user_id": 999,
        "cargo_type": "Glass",
        "date": "2020-11-03",
        "declared_value": declared_value,
    }
    request = CalcRequest(**request_json)
    response = await insurance_calculation(db_sess=fake_sess, calc_in=request)

    expect_json = {
        "request": request,
        "insurance_value": round(declared_value * rate.rate, 2),
    }
    assert expect_json == response


@pytest.mark.asyncio
async def test_get_rate_no_rate(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    rate = None
    mocker.patch(
        "api.v1.routes.insurance_calc.get_insurance_rate_for_calc",
        new_callable=mocker.AsyncMock,
        return_value=rate,
    )
    request_json = {
        "user_id": 999,
        "cargo_type": "Glass",
        "date": "2020-11-03",
        "declared_value": 3000,
    }
    request = CalcRequest(**request_json)

    with pytest.raises(HTTPException) as exc:
        await insurance_calculation(db_sess=fake_sess, calc_in=request)
    assert exc.value.status_code == 404
    assert (
        exc.value.detail
        == f"insurance rate for {request_json["cargo_type"]} on {request_json["date"]} not found"
    )
