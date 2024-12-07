from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_helper
from app.crud.rate import bulk_load_rates
from app.utils.files_utils import json_read
from app.core import settings

router = APIRouter(prefix="/administration", tags=["Administration"])


@router.get("/import_rates/", status_code=status.HTTP_204_NO_CONTENT)
async def import_rates(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    rates_dict = json_read(settings.import_.path)
    if not await bulk_load_rates(db_sess, rates_dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="import operation went wrong",
        )
