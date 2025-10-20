import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from api import router as api_router
from core import settings
from fastapi import FastAPI
from services import kafka
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await kafka.producer.start()
    yield
    await kafka.producer.stop()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
