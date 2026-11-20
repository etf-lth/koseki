import math
from typing import Generic, TypeVar
from typing_extensions import TypedDict
from sqlalchemy.orm import Query

T = TypeVar("T")

PAGINATION_DEFAULT_PER_PAGE = 100

class Page(TypedDict, Generic[T]):
    items: list[T]
    page: int
    per_page: int
    total: int
    pages: int
    has_prev: bool
    has_next: bool
    prev_num: int | None
    next_num: int | None

def paginate(query: Query[T], page: int | None = 1, per_page: int = PAGINATION_DEFAULT_PER_PAGE) -> Page[T]:
    page = max(1, page or 1)
    per_page = max(1, per_page)

    total = query.order_by(None).count()
    pages = math.ceil(total / per_page)

    page = min(page, max(1, pages))

    items = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_prev": page > 1,
        "has_next": page < pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < pages else None,
    }