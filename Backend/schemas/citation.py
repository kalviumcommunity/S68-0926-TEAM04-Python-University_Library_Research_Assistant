# pyright: reportMissingImports=false
from pydantic import BaseModel


class Citation(BaseModel):
    document_id: str
    title: str
    page: int | None = None
    section: str | None = None
    