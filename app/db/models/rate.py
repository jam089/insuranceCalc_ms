from datetime import date

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from .base import Base


class Rate(Base):
    __tablename__ = "insurance_rates"
    __table_args__ = (
        UniqueConstraint("date", "cargo_type", name="uix_date_cargo_type"),
    )

    date: Mapped[date]
    cargo_type: Mapped[str]
    rate: Mapped[float]
