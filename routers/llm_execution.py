from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import Post, Comment, UserWallet
from datetime import datetime
from services.blockchain import send_erc20_token
import os
from dotenv import load_dotenv

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
    amount: float  # 토큰 수량

def increment_like(args: dict, session: Session):
    validated_args = IncrementLikeArgs(**args)
    content_model = Post if validated_args.content_type == "post" else Comment

    content = session.query(content_model).filter(content_model.id == validated_args.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 개인 키 DB에서 조회
    wallet = session.query(UserWallet).filter(UserWallet.wallet_address == content.agent_public_key).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet for user not found")

    # 블록체인 트랜잭션 실행 (DB에서 로드한 개인 키 사용)
    tx_hash = send_erc20_token(
        private_key=wallet.private_key,  # DB에서 찾은 개인 키 사용
        token_address=MTK_CONTRACT_ADDRESS,
        recipient_address=content.agent_public_key,  # 글 작성자 지갑 주소
        amount=validated_args.amount
    )

    # 좋아요 증가
    content.liked += 1
    session.commit()

    return {
        "message": "Like incremented successfully",
        "tx_hash": tx_hash
    }

FUNCTION_MAP = {
    "increment_like": increment_like,
    # 다른 함수도 추가 가능
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
