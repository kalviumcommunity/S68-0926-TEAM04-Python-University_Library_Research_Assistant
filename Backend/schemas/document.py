from pydantic import BaseModel


class Document(BaseModel):
    document_id: str
    title: str
    document_type: str | None = None
    author: str | None = None
    year: int | None = None