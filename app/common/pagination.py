"""Simple pagination helpers for list endpoints."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PaginationParams:
    """Validated pagination parameters."""

    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination_params(
    page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> PaginationParams:
    """Return bounded pagination parameters for FastAPI dependencies."""
    return PaginationParams(page=page, page_size=page_size)
