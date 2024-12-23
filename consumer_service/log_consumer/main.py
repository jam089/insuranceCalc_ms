from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from api import router as api_router
from services import kafka
from core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka.consumer.start()
    yield
    await kafka.consumer.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        log_level=logging.DEBUG,
    )
