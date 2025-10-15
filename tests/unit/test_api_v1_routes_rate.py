import pytest
from api.v1.routes.rate import update_rate
from api.v1.schemas.rate import UpdateRate
from fastapi import Response
from pytest_mock import AsyncMockType, MockFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_update_rate_exist(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    mocker.patch(
        "api.v1.routes.rate.rate_crud.get_insurance_rate_by_id",
        new_callable=mocker.AsyncMock,
        return_value=3,
    )
    fake_update_insurance_rate: AsyncMockType = mocker.patch(
        "api.v1.routes.rate.rate_crud.update_insurance_rate",
        new_callable=mocker.AsyncMock,
    )
    fake_update_create_insurance_rate: AsyncMockType = mocker.patch(
        "api.v1.routes.rate.rate_crud.create_insurance_rate",
        new_callable=mocker.AsyncMock,
    )
    request_json = {
        "rate": "0.01",
        "cargo_type": "Glass",
        "date": "2020-03-05",
    }
    request = UpdateRate(**request_json)
    response = Response()
    await update_rate(
        db_sess=fake_sess,
        rate_id=3,
        rate_in=request,
        response=response,
    )
    fake_update_insurance_rate.assert_awaited_once()
    fake_update_create_insurance_rate.assert_not_awaited()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_rate_non_exist(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    mocker.patch(
        "api.v1.routes.rate.rate_crud.get_insurance_rate_by_id",
        new_callable=mocker.AsyncMock,
        return_value=None,
    )
    fake_update_insurance_rate: AsyncMockType = mocker.patch(
        "api.v1.routes.rate.rate_crud.update_insurance_rate",
        new_callable=mocker.AsyncMock,
    )
    fake_update_create_insurance_rate: AsyncMockType = mocker.patch(
        "api.v1.routes.rate.rate_crud.create_insurance_rate",
        new_callable=mocker.AsyncMock,
    )
    request_json = {
        "rate": "0.01",
        "cargo_type": "Glass",
        "date": "2020-03-05",
    }
    request = UpdateRate(**request_json)
    response = Response()
    await update_rate(
        db_sess=fake_sess,
        rate_id=3,
        rate_in=request,
        response=response,
    )
    fake_update_insurance_rate.assert_not_awaited()
    fake_update_create_insurance_rate.assert_awaited_once()
    assert response.status_code == 201
