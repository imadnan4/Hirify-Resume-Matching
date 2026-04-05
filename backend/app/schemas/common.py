from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


def build_page(*, items, total: int, skip: int, limit: int) -> PaginatedResponse:
    page = (skip // limit) + 1 if limit else 1
    pages = (total + limit - 1) // limit if limit else 0
    return PaginatedResponse(items=items, total=total, page=page, size=limit, pages=pages)
