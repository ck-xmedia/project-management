from __future__ import annotations

from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")


def paginate(items: Iterable[T], limit: int, offset: int) -> Tuple[list[T], int]:
    lst = list(items)
    total = len(lst)
    return lst[offset : offset + limit], total
