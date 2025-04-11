from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content: str
    hash: str
    liked: bool = Field(default=False)

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content: str
    hash: str
    liked: bool = Field(default=False)

    post_id: int = Field(foreign_key="post.id")  # 본문 테이블과 연결
