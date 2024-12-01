from datetime import date

from sqlalchemy.orm import Mapped

from .base import Base


class Rate(Base):
    __tablename__ = "insurance_rates"

    data: Mapped[date]
    cargo_type: Mapped[str]
    rate: Mapped[float]
