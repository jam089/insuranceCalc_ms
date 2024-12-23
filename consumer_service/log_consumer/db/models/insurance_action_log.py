from datetime import datetime

from sqlalchemy import DateTime, TypeDecorator, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class DateTimeString(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return value


class IntegerString(TypeDecorator):
    impl = Integer

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return value


class InsuranceActionLog(Base):
    __tablename__ = "insurance_action_logs"

    user_id: Mapped[int | None] = mapped_column(IntegerString, default=None)
    action: Mapped[str]
    date_time: Mapped[datetime] = mapped_column(DateTimeString)

    @classmethod
    def __default_order_by__(cls):
        return [cls.date_time.desc()]
