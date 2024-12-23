import logging
from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult, insert
from sqlalchemy.exc import SQLAlchemyError

from log_consumer.db.models import InsuranceActionLog


logger = logging.getLogger("uvicorn")


async def get_logs(
    db_sess: AsyncSession,
    action: str | None,
    start_datetime: datetime | None,
    end_datetime: datetime | None,
) -> Sequence[InsuranceActionLog]:
    conditions = []
    if action:
        conditions.append(InsuranceActionLog.action == action)
    if start_datetime:
        conditions.append(InsuranceActionLog.date_time >= start_datetime)
    if end_datetime:
        conditions.append(InsuranceActionLog.date_time <= end_datetime)

    stmt = select(InsuranceActionLog).where(*conditions)
    result: ScalarResult = await db_sess.scalars(stmt)
    return result.all()


async def get_last_logs(
    db_sess: AsyncSession,
    limit: int,
) -> Sequence[InsuranceActionLog]:
    stmt = select(InsuranceActionLog).limit(limit=limit)
    result: ScalarResult = await db_sess.scalars(stmt)
    return result.all()


async def bulk_load_logs(
    db_sess: AsyncSession,
    logs: list,
) -> bool:
    try:
        stmt = insert(InsuranceActionLog).values(logs)
        await db_sess.execute(stmt)
        await db_sess.commit()

        return True

    except SQLAlchemyError as ex:
        logger.error(ex.args)
        await db_sess.rollback()
        return False
