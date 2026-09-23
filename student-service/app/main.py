import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.routers import students
from app.storage import ensure_container_exists


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def initialise_database() -> None:
    maximum_attempts = 10
    retry_delay_seconds = 5

    for attempt in range(1, maximum_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)

            logger.info(
                "Database connection established successfully."
            )

            return

        except OperationalError:
            logger.warning(
                "Database connection failed. Attempt %s of %s.",
                attempt,
                maximum_attempts,
            )

            if attempt == maximum_attempts:
                logger.exception(
                    "Unable to connect to the database."
                )
                raise

            time.sleep(retry_delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()

    try:
        ensure_container_exists()

        logger.info(
            "Azure Blob Storage container is ready."
        )
    except Exception:
        logger.warning(
            "Azure Blob Storage is unavailable. "
            "The service will run, but profile-photo "
            "uploads may fail."
        )

    yield


app = FastAPI(
    title="KoalaTech University Student Service",
    description=(
        "Manages student records and student profile photos "
        "for KoalaTech University."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(students.router)


@app.get(
    "/",
    tags=["Health"],
)
def root() -> dict[str, str]:
    return {
        "message": (
            "KoalaTech University Student Service is running."
        )
    }


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    if os.getenv("FORCE_UNHEALTHY") == "true":
        logger.error(
            "FORCE_UNHEALTHY active — returning HTTP 503 for /health"
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "student-service",
            },
        )

    return {
        "status": "healthy",
        "service": "student-service",
    }