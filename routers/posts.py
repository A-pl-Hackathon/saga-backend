from fastapi import APIRouter, Depends, Form
from sqlmodel import Session
from database.connection import get_session
from models.models import Post
from datetime import datetime

router = APIRouter()

# 본문 작성 API (Form 데이터 입력)
@router.post("/write")
def create_post(
    agent_public_key: str = Form(...),
    content: str = Form(...),
    hash: str = Form(...),
    session: Session = Depends(get_session)
):
    new_post = Post(
        agent_public_key=agent_public_key,
        content=content,
        hash=hash,
        created_at=datetime.utcnow(),
        liked=0
    )
    session.add(new_post)
    session.commit()
    session.refresh(new_post)

    return {
        "message": "✅ Post created successfully",
        "post": new_post
    }

# 본문 조회 (테스트 용)
@router.get("/")
def get_posts(session: Session = Depends(get_session)):
    return session.query(Post).all()
