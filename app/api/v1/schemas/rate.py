from datetime import date

from pydantic import BaseModel


class BaseRate(BaseModel):
    date: date
    cargo_type: str
    rate: float


class CreateRate(BaseRate):
    pass


class UpdateRate(BaseRate):
    pass
