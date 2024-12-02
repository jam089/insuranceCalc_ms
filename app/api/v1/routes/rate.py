import logging
from typing import Sequence, Annotated
from datetime import datetime

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import ViewRate, CreateRate
from db import db_helper
from db.models import Rate
from api.v1 import deps
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


@router.get("/{rate_id}/", response_model=ViewRate)
async def get_rate_by_id(
    rate: Annotated[Rate, Depends(deps.get_rate)],
):
    return rate


@router.post("/", response_model=ViewRate, status_code=status.HTTP_201_CREATED)
async def create_rate(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate_in: CreateRate,
):
    return await rate_crud.create_insurance_rate(db_sess, rate_in)
