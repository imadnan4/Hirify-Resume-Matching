from __future__ import annotations

from typing import Any

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator

try:
    from pgvector.sqlalchemy import Vector

    PGVECTOR_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency at runtime
    Vector = None
    PGVECTOR_AVAILABLE = False


class VectorOrJSON(TypeDecorator[list[float] | None]):
    cache_ok = True
    impl = JSON

    def __init__(self, dimensions: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PGVECTOR_AVAILABLE:
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and PGVECTOR_AVAILABLE:
            return list(value)
        return list(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return list(value)
