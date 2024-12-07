from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from log_consumer.db.models import InsuranceActionLog


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
