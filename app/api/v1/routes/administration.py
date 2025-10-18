from typing import Annotated

from core import settings
from crud.rate import bulk_load_rates
from db import db_helper
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils.files_utils import json_read

router = APIRouter(prefix="/administration", tags=["Administration"])


@router.get("/import_rates/", status_code=status.HTTP_204_NO_CONTENT)
async def import_rates(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> None:
    try:
        rates_dict = json_read(settings.import_.path)
    except FileNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_INTERNAL_SERVER_ERROR,
            detail="file with data not found",
        ) from err
    if not await bulk_load_rates(db_sess, rates_dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="import operation went wrong",
        )
