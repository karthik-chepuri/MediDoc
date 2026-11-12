import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.db import check_db, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("carebot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        log.info("pgvector extension ready")
    except Exception as exc:
        log.warning("DB init skipped: %s", exc)
    yield


app = FastAPI(title="CareBot", version="0.0.1", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "carebot"}


@app.get("/health/db")
def health_db():
    return check_db()
