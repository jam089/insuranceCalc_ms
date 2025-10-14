import logging
from datetime import datetime
from datetime import date as datetime_date
from typing import Sequence

from sqlalchemy import select, Result, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from db.models import Rate
from api.v1.schemas import CalcRequest, CreateRate, UpdateRate, UpdateRatePartial
from services import kafka

logger = logging.getLogger("uvicorn")


async def get_insurance_rate_for_calc(
    db_sess: AsyncSession,
    calc_request_in: CalcRequest,
) -> Rate | None:
    stmt = select(Rate).where(
        and_(
            Rate.date == calc_request_in.date,
            Rate.cargo_type == calc_request_in.cargo_type,
        )
    )
    result: Result = await db_sess.execute(stmt)
    rate = result.scalar()

    await kafka.producer.k_logger(
        user_id=calc_request_in.user_id,
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


async def create_insurance_rate(
    db_sess: AsyncSession,
    rate_in: CreateRate | UpdateRate,
) -> Rate:
    new_rate = Rate(**rate_in.model_dump())
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
    rate_in: UpdateRate | UpdateRatePartial,
    partial: bool = False,
) -> Rate:
    for name, value in rate_in.model_dump(exclude_unset=partial).items():
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
