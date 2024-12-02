import logging
from typing import Sequence, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import ViewRate
from db import db_helper
from crud import rate as rate_crud


logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/rate", tags=["Insurance Rates"])


@router.get("/date/{date}/", response_model=Sequence[ViewRate])
async def get_rate_by_date(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    date: str,
):
    logger.critical(date)
    return await rate_crud.get_insurance_rate_by_date(
        db_sess,
        date=datetime.strptime(date, "%Y-%m-%d").date(),
    )
