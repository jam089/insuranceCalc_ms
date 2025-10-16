from typing import Awaitable, Callable

import pytest_asyncio
from db.models import Rate
from pytest import FixtureRequest

from tests.integration.containers import (  # noqa: F401
    app_container,
    compose_containers,
    kafka_broker_container,
    pg_container,
)
from tests.integration.database import (  # noqa: F401
    async_client,
    create_test_engine,
    create_test_session_factory,
    override_dependency,
    prepare_db,
    test_session,
)
from tests.integration.factories import RateFactory, create_from_factory  # noqa: F401


@pytest_asyncio.fixture()
async def test_rate_a(
    create_from_factory: Callable[..., Awaitable[Rate]],  # noqa: F811
) -> Rate:
    rate = await create_from_factory(RateFactory)
    return rate


@pytest_asyncio.fixture()
async def test_rate_b(
    create_from_factory: Callable[..., Awaitable[Rate]],  # noqa: F811
) -> Rate:
    rate = await create_from_factory(RateFactory)
    return rate


@pytest_asyncio.fixture()
async def test_rate_c(
    create_from_factory: Callable[..., Awaitable[Rate]],  # noqa: F811
) -> Rate:
    rate = await create_from_factory(RateFactory)
    return rate


@pytest_asyncio.fixture(params=["test_rate_a", "test_rate_b", "test_rate_c"])
async def test_rates(
    request: FixtureRequest,
    test_rate_a: Rate,
    test_rate_b: Rate,
    test_rate_c: Rate,
) -> Rate:
    if request.param == "test_rate_a":
        return test_rate_a
    elif request.param == "test_rate_b":
        return test_rate_b
    else:
        return test_rate_c
