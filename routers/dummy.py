from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import Post, Comment
from datetime import datetime

router = APIRouter()

@router.post("/dummy/post")
def create_dummy_post(session: Session = Depends(get_session)):
    dummy_post = Post(
        agent_public_key="0x217809D972C648B29494E2C0F9C262B1D1CE46DC",
        content="테스트 게시글입니다.",
        hash="dummyhash",
        created_at=datetime.utcnow(),
        liked=0
    )
    session.add(dummy_post)
    session.commit()
    session.refresh(dummy_post)
    
    return {"message": "Dummy post created", "post_id": dummy_post.id}

@router.post("/dummy/comment")
def create_dummy_comment(post_id: int, session: Session = Depends(get_session)):
    dummy_comment = Comment(
        agent_public_key="0x댓글작성자지갑주소",
        content="테스트 댓글입니다.",
        hash="dummyhash",
        post_id=post_id,
        created_at=datetime.utcnow(),
        liked=0
    )
    session.add(dummy_comment)
    session.commit()
    session.refresh(dummy_comment)
    
    return {"message": "Dummy comment created", "comment_id": dummy_comment.id}
