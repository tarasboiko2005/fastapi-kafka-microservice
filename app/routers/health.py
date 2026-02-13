from fastapi import APIRouter, status, Response
from sqlalchemy import text
from app.database import engine
from app.kafka_client import producer
import logging

router = APIRouter(prefix="/health", tags=["System Health"])
logger = logging.getLogger("microservice")


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return {"status": "alive"}


@router.get("/ready")
async def readiness_probe(response: Response):
    checks = {
        "database": False,
        "kafka": False
    }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"❌ Readiness check failed: Database is down. {e}")

    if producer and producer.client:
        checks["kafka"] = True
    else:
        logger.error("❌ Readiness check failed: Kafka producer is not connected.")

    if not all(checks.values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unready", "details": checks}

    return {"status": "ready", "details": checks}