from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class InsuranceActionLog(Base):
    __tablename__ = "insurance_action_logs"

    user_id: Mapped[int | None] = mapped_column(default=None)
    action: Mapped[str]
    date_time: Mapped[datetime] = mapped_column(DateTime)

    @classmethod
    def __default_order_by__(cls):
        return [cls.date_time.desc()]
