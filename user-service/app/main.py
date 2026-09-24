import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine
from app.models import User, UserRole
from app.routers import auth, users
from app.security import hash_password


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


def create_default_admin() -> None:
    admin_username = os.getenv(
        "DEFAULT_ADMIN_USERNAME",
        "admin",
    )

    admin_email = os.getenv(
        "DEFAULT_ADMIN_EMAIL",
        "admin@koalatech.edu.au",
    )

    admin_password = os.getenv(
        "DEFAULT_ADMIN_PASSWORD",
        "AdminPassword123!",
    )

    with Session(engine) as db:
        existing_admin = db.scalar(
            select(User).where(
                User.username == admin_username
            )
        )

        if existing_admin is not None:
            logger.info(
                "Default administrator account already exists."
            )
            return

        admin = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()

        logger.info(
            "Default administrator account created."
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    create_default_admin()

    yield


app = FastAPI(
    title="KoalaTech University User Service",
    description=(
        "Manages user accounts, authentication and "
        "role-based access for KoalaTech University."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(auth.router)
app.include_router(users.router)


@app.get(
    "/",
    tags=["Health"],
)
def root() -> dict[str, str]:
    return {
        "message": "KoalaTech University User Service is running."
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
                "service": "user-service",
            },
        )

    return {
        "status": "healthy",
        "service": "user-service",
    }


@app.get(
    "/demo/error",
    tags=["Health"],
)
def demo_error():
    if os.getenv("ENABLE_DEMO_ERRORS") != "true":
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found"},
        )

    logger.error(
        "demo /demo/error — returning HTTP 500 while /health stays 200"
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "service": "user-service",
        },
    )