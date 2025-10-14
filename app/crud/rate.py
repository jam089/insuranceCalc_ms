import logging
from datetime import date as datetime_date
from datetime import datetime
from typing import Sequence, Any

from db.models import Rate
from services import kafka
from sqlalchemy import Result, and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("uvicorn")


async def get_insurance_rate_for_calc(
    db_sess: AsyncSession,
    date: datetime_date,
    cargo_type: str,
    user_id: int,
) -> Rate | None:
    stmt = select(Rate).where(
        and_(
            Rate.date == date,
            Rate.cargo_type == cargo_type,
        )
    )
    result: Result = await db_sess.execute(stmt)
    rate = result.scalar()

    await kafka.producer.k_logger(
        user_id=user_id,
        date_time=datetime.now(),
        crud_action="get_insurance_rate_for_calc",
    )

    return rate


async def get_insurance_rate_by_id(
    db_sess: AsyncSession,
    rate_id: int,
) -> Rate | None:
    rate = await db_sess.get(Rate, rate_id)
    return rate


async def get_insurance_rate_by_date(
    db_sess: AsyncSession,
    date: datetime_date,
) -> Sequence[Rate]:
    stmt = select(Rate).where(Rate.date == date)
    result = await db_sess.execute(stmt)
    rate_list = result.scalars().all()
    return rate_list


async def create_insurance_rate(db_sess: AsyncSession, rate_in: dict[str, Any]) -> Rate:
    new_rate = Rate(**rate_in)
    db_sess.add(new_rate)
    await db_sess.commit()
    await db_sess.refresh(new_rate)

    await kafka.producer.k_logger(
        date_time=datetime.now(),
        crud_action="create_insurance_rate",
    )

    return new_rate


async def update_insurance_rate(
    db_sess: AsyncSession,
    rate: Rate,
    rate_in: dict[str, Any],
) -> Rate:
    for name, value in rate_in.items():
        setattr(rate, name, value)
    await db_sess.commit()
    await db_sess.refresh(rate)

    await kafka.producer.k_logger(
        date_time=datetime.now(),
        crud_action="update_insurance_rate",
    )

    return rate


async def delete_insurance_rate(
    db_sess: AsyncSession,
    rate: Rate,
) -> None:
    await db_sess.delete(rate)
    await db_sess.commit()

    await kafka.producer.k_logger(
        date_time=datetime.now(),
        crud_action="delete_insurance_rate",
    )


async def bulk_load_rates(
    db_sess: AsyncSession,
    rates_dict: dict,
) -> bool:
    try:
        rates_of_date_list = []
        for date, rates_of_date in rates_dict.items():  # type: (str, list)
            rates_of_date_list.extend(
                [
                    {
                        "date": datetime.strptime(date, "%Y-%m-%d").date(),
                        "cargo_type": rate_item.get("cargo_type"),
                        "rate": float(rate_item.get("rate")),
                    }
                    for rate_item in rates_of_date
                ]
            )
        stmt = insert(Rate).values(rates_of_date_list)
        stmt = stmt.on_conflict_do_update(
            index_elements=["date", "cargo_type"],
            set_={
                "rate": stmt.excluded.rate,
            },
        )
        await db_sess.execute(stmt)
        await db_sess.commit()

        await kafka.producer.k_logger(
            date_time=datetime.now(), crud_action="bulk_load_rates"
        )

        return True

    except SQLAlchemyError as ex:
        logger.error(ex.args)
        await db_sess.rollback()
        return False
