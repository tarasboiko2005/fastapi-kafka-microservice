from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
from app.kafka_client import start_kafka_producer, stop_kafka_producer
from app.routers import orders, users
from app.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_kafka_producer()
    yield
    await stop_kafka_producer()

app = FastAPI(
    title="Microservice API",
    description="API for ordering products (FastAPI + Kafka + Postgres)",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Invalid data provided",
            "details": exc.errors()
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"🔥 Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error. Our team is working on it!"
        },
    )

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"🚀 Request: {request.method} {request.url.path} | Time: {process_time:.4f}s")
        return response

app.add_middleware(TimingMiddleware)
app.include_router(orders.router)
app.include_router(users.router)