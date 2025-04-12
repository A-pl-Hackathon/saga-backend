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
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

load_dotenv()

MTK_CONTRACT_ADDRESS = os.getenv("MTK_CONTRACT_ADDRESS")
logger.info(f"Using MTK Contract Address: {MTK_CONTRACT_ADDRESS}")

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
    try:
        logger.info(f"Increment like request: {validated_args.dict()}")
        
        content_model = Post if validated_args.content_type == "post" else Comment
        logger.info(f"Content model: {content_model.__name__}")

        content = session.query(content_model).filter(content_model.id == validated_args.content_id).first()
        if not content:
            logger.error(f"Content not found: {validated_args.content_type} with ID {validated_args.content_id}")
            raise HTTPException(status_code=404, detail="Content not found")
        logger.info(f"Found content: {content.id} by {content.agent_public_key}")

        wallet = session.query(UserWallet).filter(UserWallet.wallet_address == validated_args.wallet_address).first()
        if not wallet:
            logger.error(f"Wallet not found: {validated_args.wallet_address}")
            raise HTTPException(status_code=404, detail="Wallet for user not found")
        logger.info(f"Found wallet: {wallet.wallet_address}")
        
        # Quick key validation check
        if not wallet.private_key or len(wallet.private_key) < 64:
            logger.error(f"Invalid private key format for wallet: {wallet.wallet_address}")
            raise HTTPException(status_code=400, detail="Invalid private key format")
        
        logger.info(f"Sending token: {MTK_CONTRACT_ADDRESS} to {content.agent_public_key}, amount: 3")
        
        try:
            tx_hash = send_erc20_token(
                private_key=wallet.private_key,
                token_address=MTK_CONTRACT_ADDRESS,
                recipient_address=content.agent_public_key,
                amount=3
            )
            logger.info(f"Token transfer successful: {tx_hash}")

            # 좋아요 증가
            content.liked += 1
            session.commit()
            logger.info(f"Like incremented for {validated_args.content_type} {validated_args.content_id}")

            return {
                "message": "Like incremented successfully",
                "tx_hash": tx_hash
            }
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            error_details = str(e)
            
            if "insufficient funds" in error_details:
                logger.error(f"Insufficient funds error: {error_details}")
                raise HTTPException(status_code=400, detail=f"Insufficient ETH to pay for gas fees. Please fund your wallet with ETH to continue. Details: {error_details}")
            else:
                logger.error(f"Other blockchain error: {error_details}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Blockchain transaction error: {error_details}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in increment_like: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Function execution error: {str(e)}")

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
    logger.info(f"Function call request received: {call.function}")
    
    try:
        if call.function == "increment_like":
            logger.info(f"Processing increment_like with args: {call.arguments}")
            validated_args = IncrementLikeArgs(**call.arguments)
            result = increment_like(validated_args, session)

        elif call.function == "write_post":
            logger.info(f"Processing write_post with args: {call.arguments}")
            validated_args = WritePost(**call.arguments)
            result = write_post(validated_args, session)

        elif call.function == "write_comment":
            logger.info(f"Processing write_comment with args: {call.arguments}")
            validated_args = WriteComment(**call.arguments)
            result = write_comment(validated_args, session)

        elif call.function == "connect_db":
            logger.info("Processing connect_db request")
            result = connect_db(session)

        else:
            logger.error(f"Unknown function requested: {call.function}")
            raise HTTPException(status_code=400, detail=f"Function '{call.function}' not recognized.")

        logger.info(f"Function {call.function} executed successfully")
        return result

    except HTTPException as e:
        logger.error(f"HTTP exception in execute_function_call: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        error_msg = f"Function execution error: {str(e)}"
        logger.error(f"Unexpected exception in execute_function_call: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
