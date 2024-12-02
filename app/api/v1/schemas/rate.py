from datetime import date as datetime_date

from pydantic import BaseModel, ConfigDict


class BaseRate(BaseModel):
    date: datetime_date
    cargo_type: str
    rate: float


class CreateRate(BaseRate):
    pass


class UpdateRate(BaseRate):
    pass


class UpdateRatePartial(BaseRate):
    date: datetime_date | None = None
    cargo_type: str | None = None
    rate: int | None = None


class ViewRate(BaseRate):
    model_config = ConfigDict(from_attributes=True)

    id: int
