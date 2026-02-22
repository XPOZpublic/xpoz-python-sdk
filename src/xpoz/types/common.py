from pydantic import BaseModel


class PaginationInfo(BaseModel, extra="allow"):
    table_name: str | None = None
    total_rows: int = 0
    total_pages: int = 0
    page_number: int = 1
    page_size: int | None = None
    results_count: int = 0
