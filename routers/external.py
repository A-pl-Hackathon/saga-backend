from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import UserWallet
from schemas.external_data import ExternalData
from datetime import datetime

router = APIRouter()

@router.post("/external")
async def receive_external_data(request: ExternalData, session: Session = Depends(get_session)):
    existing_wallet = session.query(UserWallet).filter(UserWallet.wallet_address == request.personalData.walletAddress).first()

    if existing_wallet:
        raise HTTPException(status_code=400, detail="Wallet already exists")

    new_wallet = UserWallet(
        wallet_address=request.personalData.walletAddress,
        private_key=request.backendPrivateKey,  # 받은 개인 키
        created_at=datetime.utcnow()
    )

    session.add(new_wallet)
    session.commit()

    return {"message": "External data and private key received successfully."}
