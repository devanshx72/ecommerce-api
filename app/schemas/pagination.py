from pydantic import BaseModel
from typing import Any


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


def paginate(query, page: int, limit: int) -> dict:
    """Paginates any SQLAlchemy query."""
    total = query.count()
    pages = (total + limit - 1) // limit
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1
    }