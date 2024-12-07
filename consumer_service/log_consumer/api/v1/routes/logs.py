from datetime import datetime
from typing import Sequence, Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from log_consumer.db import db_helper
from log_consumer.api.v1.schemas import LogView
from log_consumer.crud import logs as logs_crud

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/", response_model=Sequence[LogView])
async def get_logs(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    action: str | None = None,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
):
    return await logs_crud.get_logs(db_sess, action, start_datetime, end_datetime)
