from pydantic import BaseModel
from sqlalchemy import select, Result, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Rate


async def get_insurance_rate_for_calc(
    db_sess: AsyncSession,
    calc_request_in: BaseModel,
) -> Rate | None:
    stmt = select(Rate).where(
        and_(
            Rate.date == calc_request_in.date,
            Rate.cargo_type == calc_request_in.cargo_type,
        )
    )
    result: Result = await db_sess.execute(stmt)
    rate = result.scalar()
    return rate
