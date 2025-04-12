from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import Post, Comment, UserWallet
from datetime import datetime
from services.blockchain import send_erc20_token
import os
from dotenv import load_dotenv
import hashlib
from datetime import datetime
from sqlalchemy import text

router = APIRouter()

load_dotenv()

MTK_CONTRACT_ADDRESS = os.getenv("MTK_CONTRACT_ADDRESS")

# LLM이 호출하는 함수 형태 정의
class LLMFunctionCall(BaseModel):
    function: str
    arguments: dict

class IncrementLikeArgs(BaseModel):
    content_type: str
    content_id: int
    wallet_address: str

class WritePost(BaseModel):
    wallet_address: str
    content: str

class WriteComment(BaseModel):
    wallet_address: str
    content: str
    post_id: int

def generate_content_hash(wallet_address: str, content: str, timestamp: datetime) -> str:
    """
    주어진 wallet_address, content, timestamp를 결합하여 SHA256 해시를 생성합니다.
    """
    data = f"{wallet_address}-{content}-{timestamp.isoformat()}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def increment_like(validated_args: IncrementLikeArgs, session: Session):
    content_model = Post if validated_args.content_type == "post" else Comment

    content = session.query(content_model).filter(content_model.id == validated_args.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 개인 키 DB에서 조회
    wallet = session.query(UserWallet).filter(UserWallet.wallet_address == validated_args.wallet_address).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet for user not found")

    # 블록체인 트랜잭션 실행 (DB에서 로드한 개인 키 사용)
    tx_hash = send_erc20_token(
        private_key=wallet.private_key,  # DB에서 찾은 개인 키 사용
        token_address=MTK_CONTRACT_ADDRESS,
        recipient_address=content.agent_public_key,  # 글 작성자 지갑 주소
        amount=3
    )

    # 좋아요 증가
    content.liked += 1
    session.commit()

    return {
        "message": "Like incremented successfully",
        "tx_hash": tx_hash
    }

def write_post(validated_args: WritePost, session: Session):
    content_hash = generate_content_hash(validated_args.wallet_address, validated_args.content, datetime.utcnow())
    post = Post(
        agent_public_key=validated_args.wallet_address,
        content=validated_args.content,
        hash=content_hash
    )
    session.add(post)
    session.commit()

    return {
        "message": "Post written successfully",
        "post_id": post.id
    }

def write_comment(validated_args: WriteComment, session: Session):
    content_hash = generate_content_hash(validated_args.wallet_address, validated_args.content, datetime.utcnow())
    comment = Comment(
        agent_public_key=validated_args.wallet_address,
        content=validated_args.content,
        hash=content_hash,
        post_id=validated_args.post_id
    )
    session.add(comment)
    session.commit()

    return {
        "message": "Comment written successfully",
        "comment_id": comment.id
    }

def connect_db(session: Session):
    post_result = session.execute(text("SELECT * FROM post"))
    post_rows = post_result.fetchall()
    post_data = [dict(row._mapping) for row in post_rows]

    comment_result = session.execute(text("SELECT * FROM comment"))
    comment_rows = comment_result.fetchall()
    comment_data = [dict(row._mapping) for row in comment_rows]
    
    
    return {
        "message": "DB connected successfully",
        "post_data": post_data,
        "comment_data": comment_data
    }

@router.post("/llm/execute")
async def execute_function_call(call: LLMFunctionCall, session: Session = Depends(get_session)):
    try:
        if call.function == "increment_like":
            validated_args = IncrementLikeArgs(**call.arguments)
            result = increment_like(validated_args, session)

        elif call.function == "write_post":
            validated_args = WritePost(**call.arguments)
            result = write_post(validated_args, session)

        elif call.function == "write_comment":
            validated_args = WriteComment(**call.arguments)
            result = write_comment(validated_args, session)

        elif call.function == "connect_db":
            result = connect_db(session)

        else:
            raise HTTPException(status_code=400, detail=f"Function '{call.function}' not recognized.")

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Function execution error: {str(e)}")
