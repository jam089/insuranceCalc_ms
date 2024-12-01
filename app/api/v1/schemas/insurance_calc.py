from datetime import date

from pydantic import BaseModel, ConfigDict


class CalcRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int | None = None
    date: date
    cargo_type: str
    declared_value: float


class CalcResponse(BaseModel):
    insurance_value: float
