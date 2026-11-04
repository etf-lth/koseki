

import math
from sqlalchemy.orm import Query

PAGINATION_DEFAULT_PER_PAGE = 100

def paginate(query: Query, page: int = 1, per_page = PAGINATION_DEFAULT_PER_PAGE) -> dict:
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