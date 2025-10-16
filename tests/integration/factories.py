import random
from collections.abc import Callable
from typing import (
    Any,
    Awaitable,
    Type,
    TypeVar,
    cast,
)

import factory
import pytest
from db.models import Rate
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

T = TypeVar("T", bound=factory.alchemy.SQLAlchemyModelFactory)


class RateFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Rate
        sqlalchemy_session_persistence = "flush"

    date = factory.Faker("date_between_dates", date_start="-25y")
    cargo_type = factory.Faker("word")
    rate = factory.LazyFunction(lambda: random.randint(5, 199) / 1000)


@pytest.fixture(scope="function")
def create_from_factory(
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> Callable[..., Awaitable[T]]:
    async def _create(
        factory_class: Type[T],
        **kwargs: Any,
    ) -> T:
        obj: T = factory_class.build(**kwargs)
        async with create_test_session_factory() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return obj

    return cast(Callable[..., Awaitable[T]], _create)
