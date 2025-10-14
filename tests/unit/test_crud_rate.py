from datetime import date

import pytest
from crud.rate import bulk_load_rates
from pytest_mock import MockFixture
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

test_json = {
    "2024-11-30": [
        {"cargo_type": "Glass", "rate": "0.015"},
        {"cargo_type": "Other", "rate": "0.04"},
    ],
    "2024-12-01": [
        {"cargo_type": "Glass", "rate": "0.01"},
    ],
}


@pytest.mark.asyncio
async def test_bulk_load_rates(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    mock_logger = mocker.patch(
        "app.crud.rate.kafka.producer.k_logger",
        new_callable=mocker.AsyncMock,
    )
    resp = await bulk_load_rates(fake_sess, test_json)

    assert resp is True

    stmt_arg = fake_sess.execute.call_args[0][0]
    compiled = stmt_arg.compile(dialect=postgresql.dialect())
    assert "Glass" in str(compiled.params.values())
    assert "Other" in str(compiled.params.values())
    assert date.fromisoformat("2024-12-01") in compiled.params.values()

    mock_logger.assert_awaited_once()

    fake_sess.execute.assert_called_once()
    fake_sess.commit.assert_called_once()
    fake_sess.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_bulk_load_rates_rolls_back_on_error(mocker: MockFixture) -> None:
    fake_sess = mocker.AsyncMock()
    mocker.patch("app.crud.rate.kafka.producer.k_logger")
    fake_sess.execute.side_effect = SQLAlchemyError("boom")

    result = await bulk_load_rates(fake_sess, {"2024-10-01": []})

    fake_sess.rollback.assert_called_once()
    fake_sess.commit.assert_not_called()
    assert result is False
