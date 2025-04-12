# routers/token_transfer.py
from fastapi import APIRouter, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import UserWallet
from services.saga_blockchain import send_saga_token

router = APIRouter()

@router.post("/transfer-token/")
def transfer_token(
    wallet_address: str = Form(...),
    recipient_address: str = Form(...),
    amount: float = Form(...),
    session: Session = Depends(get_session)
):
    try:
        wallet = session.query(UserWallet).filter(UserWallet.wallet_address == wallet_address).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        tx_hash = send_saga_token(
            private_key=wallet.private_key,
            recipient_address=recipient_address,
            amount=amount
        )
        explorer_link = f"https://explorer.saga.xyz/tx/{tx_hash}"

        return {
            "message": "Token transfer request received.",
            "tx_hash": tx_hash,
            "explorer_link": explorer_link
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
