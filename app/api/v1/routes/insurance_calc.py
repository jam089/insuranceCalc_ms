from typing import Annotated

from crud.rate import get_insurance_rate_for_calc
from db import db_helper
from db.models import Rate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import CalcRequest, CalcResponse

router = APIRouter(prefix="/insurance_calculation", tags=["Insurance Calculation"])


@router.get("/", response_model=CalcResponse)
async def insurance_calculation(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    calc_in: CalcRequest = Depends(),  # noqa: B008
) -> dict[str, CalcRequest | float]:
    rate: Rate | None = await get_insurance_rate_for_calc(
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
