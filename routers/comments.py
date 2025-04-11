from fastapi import APIRouter, Depends, Form
from sqlmodel import Session
from database.connection import get_session
from models.models import Comment
from datetime import datetime

router = APIRouter()

# 댓글 작성 API (Form 데이터 입력)
@router.post("/write")
def create_comment(
    agent_public_key: str = Form(...),
    content: str = Form(...),
    hash: str = Form(...),
    post_id: int = Form(...),  # 댓글이 속한 본문의 id
    session: Session = Depends(get_session)
):
    new_comment = Comment(
        agent_public_key=agent_public_key,
        content=content,
        hash=hash,
        post_id=post_id,
        created_at=datetime.utcnow(),
        liked=False
    )
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)

    return {
        "message": "✅ Comment created successfully",
        "comment": new_comment
    }

# 댓글 조회 (테스트 용)
@router.get("/")
def get_comments(session: Session = Depends(get_session)):
    return session.query(Comment).all()

