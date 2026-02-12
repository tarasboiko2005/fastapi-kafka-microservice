from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.kafka_client import start_kafka_producer, stop_kafka_producer
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
from app.routers import orders, users
import logging

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await start_kafka_producer()
    yield
    await stop_kafka_producer()

app = FastAPI(
    title="Microservice API",
    description="This is an API for ordering products written in FastAPI + Kafka.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Path: {request.url.path} | Time: {process_time:.4f}s")

        return response

app.add_middleware(TimingMiddleware)
app.include_router(orders.router)
app.include_router(users.router)