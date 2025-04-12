from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import Post, Comment
from datetime import datetime
from sqlmodel import SQLModel, Field
from services.blockchain import send_erc20_token
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
MTK_CONTRACT_ADDRESS = os.getenv("MTK_CONTRACT_ADDRESS")

# LLM이 호출하는 함수 형태 정의
class LLMFunctionCall(BaseModel):
    function: str
    arguments: dict

# Increment Like 함수의 인자 정의
class IncrementLikeArgs(BaseModel):
    content_type: str
    content_id: int
    from_wallet: str
    amount: float

# Create Post 함수의 인자 정의 (예시)
class CreatePostArgs(BaseModel):
    agent_public_key: str
    content: str
    hash: str

# 실제 기능 구현
def increment_like(args: dict, session: Session):
    validated_args = IncrementLikeArgs(**args)
    content_model = Post if validated_args.content_type == "post" else Comment

    content = session.query(content_model).filter(content_model.id == validated_args.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 블록체인 트랜잭션 실행
    tx_hash = send_erc20_token(
        token_address=MTK_CONTRACT_ADDRESS,  # MTK 주소를 .env에서 불러오기
        recipient_address=content.agent_public_key,  # 받는 사람의 지갑 주소 (글 작성자)
        amount=validated_args.amount
    )

    # 좋아요 증가
    content.liked += 1
    session.commit()

    return {
        "message": "Like incremented successfully",
        "tx_hash": tx_hash
    }

def create_post(args: dict, session: Session):
    validated_args = CreatePostArgs(**args)
    new_post = Post(
        agent_public_key=validated_args.agent_public_key,
        content=validated_args.content,
        hash=validated_args.hash,
        created_at=datetime.utcnow()
    )

    session.add(new_post)
    session.commit()
    session.refresh(new_post)

    return {
        "message": "Post created successfully",
        "post_id": new_post.id
    }

# 여기에 추가적인 함수들(create_comment 등)을 정의 가능

# 함수 이름과 실제 함수를 매핑
FUNCTION_MAP = {
    "increment_like": increment_like,
    "create_post": create_post,
    # 추가 함수 정의 시 여기에 계속 추가하면 됩니다.
}

@router.post("/llm/execute")
async def execute_function_call(call: LLMFunctionCall, session: Session = Depends(get_session)):
    func = FUNCTION_MAP.get(call.function)

    if not func:
        raise HTTPException(status_code=400, detail=f"Function '{call.function}' not recognized.")

    try:
        result = func(call.arguments, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Function execution error: {str(e)}")
