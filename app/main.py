import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from aiokafka.errors import KafkaConnectionError
from fastapi import FastAPI

from core import settings
from api import router as api_router
from services import kafka

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await kafka.producer.start()
        asyncio.create_task(kafka.producer.batch_sender())
    except KafkaConnectionError as ex:
        logger.critical(ex.args)
    yield
    await kafka.producer.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
