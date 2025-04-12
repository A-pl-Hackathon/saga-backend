from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content: str
    hash: str
    liked: int = Field(default=0)

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content: str
    hash: str
    liked: int = Field(default=0)

    post_id: int = Field(foreign_key="post.id")  # 본문 테이블과 연결

class UserWallet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_address: str = Field(index=True, unique=True)
    private_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)