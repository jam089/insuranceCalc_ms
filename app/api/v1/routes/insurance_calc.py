from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_helper
from api.v1.schemas import CalcResponse, CalcRequest
from crud.rate import get_insurance_rate_for_calc
from db.models import Rate

router = APIRouter(prefix="/insurance_calculation", tags=["Insurance Calculation"])


@router.post("/", response_model=CalcResponse)
async def insurance_calculation(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    calc_in: CalcRequest,
):
    rate: Rate = await get_insurance_rate_for_calc(
        db_sess,
        calc_request_in=calc_in,
    )

    if rate:
        insurance_value = round(calc_in.declared_value * rate.rate, 2)
        return {
            "request": calc_in,
            "insurance_value": insurance_value,
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"insurance rate for {calc_in.cargo_type} "
        f"on {calc_in.date} not found",
    )
