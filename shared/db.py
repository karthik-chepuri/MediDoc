"""Postgres + pgvector connection helpers (decision D-004)."""
import os

from sqlalchemy import create_engine, text


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/suja")
    # Hosted providers (e.g. Neon) may give postgres:// or postgresql://; SQLAlchemy needs a driver name.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


engine = create_engine(_database_url(), pool_pre_ping=True)


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def check_db() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            has_vector = (
                conn.execute(
                    text("SELECT count(*) FROM pg_extension WHERE extname = 'vector'")
                ).scalar()
                == 1
            )
        return {"db": "ok", "pgvector": has_vector}
    except Exception as exc:  # report, don't crash the health endpoint
        return {"db": "error", "detail": str(exc)}
