from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int | None
    action: str
    date_time: datetime
