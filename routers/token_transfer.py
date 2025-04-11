# routers/token_transfer.py
from fastapi import APIRouter, HTTPException, Form
from services.blockchain import send_erc20_token

router = APIRouter()

@router.post("/transfer-token/")
def transfer_token(
    token_address: str = Form(...),
    recipient_address: str = Form(...),
    amount: str = Form(...)
):
    try:
        tx_hash = send_erc20_token(token_address, recipient_address, amount)
        explorer_link = f"https://sepolia.etherscan.io/tx/{tx_hash}"

        return {
            "message": "토큰 전송이 성공적으로 요청되었습니다.",
            "tx_hash": tx_hash,
            "explorer_link": explorer_link
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
