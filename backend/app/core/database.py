from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base


engine_kwargs: dict[str, object] = {"echo": settings.sql_echo}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
    )

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):  # pragma: no cover - runtime hook
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            try:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception:
                # The app can still function without the extension when using JSON fallback.
                pass
    try:
        import alembic.config
        import alembic.command
        from pathlib import Path as _Path
        alembic_cfg = alembic.config.Config(str(_Path(__file__).resolve().parents[2] / "alembic.ini"))
        alembic.command.upgrade(alembic_cfg, "head")
    except Exception:
        import logging
        _logger = logging.getLogger(__name__)
        _logger.exception("Alembic upgrade failed; falling back to create_all")
        Base.metadata.create_all(bind=engine)
