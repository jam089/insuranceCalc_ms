import logging
from datetime import datetime
from typing import Annotated, Sequence

from crud import rate as rate_crud
from db import db_helper
from db.models import Rate
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1 import deps
from api.v1.schemas import CreateRate, UpdateRate, UpdateRatePartial, ViewRate

logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/rates", tags=["Insurance Rates"])


@router.get("/{rate_id}/", response_model=ViewRate)
async def get_rate_by_id(
    rate: Annotated[Rate, Depends(deps.get_rate)],
) -> Rate:
    return rate


@router.get("/", response_model=Sequence[ViewRate])
async def get_rate_by_date(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    date: str,
) -> Sequence[Rate]:
    return await rate_crud.get_insurance_rate_by_date(
        db_sess,
        date=datetime.strptime(date, "%Y-%m-%d").date(),
    )


@router.post("/", response_model=ViewRate, status_code=status.HTTP_201_CREATED)
async def create_rate(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate_in: CreateRate,
) -> Rate:
    return await rate_crud.create_insurance_rate(db_sess, rate_in)


@router.put("/{rate_id}/", response_model=ViewRate)
async def update_rate(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate_id: int,
    rate_in: UpdateRate,
    response: Response,
) -> Rate:
    rate = await rate_crud.get_insurance_rate_by_id(db_sess, rate_id)
    if rate:
        return await rate_crud.update_insurance_rate(db_sess, rate, rate_in)

    response.status_code = status.HTTP_201_CREATED
    return await rate_crud.create_insurance_rate(db_sess, rate_in)


@router.patch("/{rate_id}/", response_model=ViewRate)
async def update_rate_partial(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate: Annotated[Rate, Depends(deps.get_rate)],
    rate_in: UpdateRatePartial,
) -> Rate:
    return await rate_crud.update_insurance_rate(
        db_sess,
        rate,
        rate_in,
        partial=True,
    )


@router.delete("/{rate_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    rate: Annotated[Rate, Depends(deps.get_rate)],
) -> None:
    await rate_crud.delete_insurance_rate(db_sess, rate)
