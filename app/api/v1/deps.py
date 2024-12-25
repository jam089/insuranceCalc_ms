from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_helper
from crud.rate import get_insurance_rate_by_id
from db.models import Rate


async def get_rate(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate_id: int,
) -> Rate:
    rate = await get_insurance_rate_by_id(db_sess, rate_id)

    if rate:
        return rate

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"insurance rate with id=[{rate_id}] not found",
    )
