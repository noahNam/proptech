from datetime import datetime
from pydantic import BaseModel


class ArticleEntity(BaseModel):
    id: int
    post_id: int
    body: str
    created_at: datetime
    updated_at: datetime
