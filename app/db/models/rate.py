from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Rate(Base):
    __tablename__ = "insurance_rates"

    date: Mapped[date] = mapped_column(Date, unique=True)
    cargo_type: Mapped[str]
    rate: Mapped[float]
