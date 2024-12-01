from fastapi import APIRouter

from api.v1.schemas import CalcResponse, CalcRequest

router = APIRouter(prefix="/calc", tags=["Insurance Calculation"])

MOCK_RATE = 0.5


@router.post("/", response_model=CalcResponse)
async def insurance_calculation(
    calc_in: CalcRequest,
):
    insurance_value = calc_in.declared_value * MOCK_RATE
    return {
        "insurance_value": insurance_value,
    }
