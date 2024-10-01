from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostCreate(BaseModel):
    content: Optional[str] = None
    image: str
    location: Optional[str] = None


class Post(PostCreate):
    id: int
    author_id: int
    created_dt: datetime

    class Config:
        from_attributes = True
        # orm_mode = True
