from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from log_consumer.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
    )
