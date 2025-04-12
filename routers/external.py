from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_session
from models.models import UserWallet
from schemas.external_data import ExternalData
from datetime import datetime
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/external")
async def receive_external_data(request: ExternalData, session: Session = Depends(get_session)):
    logger.info(f"Received external data: {request.dict()}")
    
    existing_wallet = session.query(UserWallet).filter(UserWallet.wallet_address == request.personalData.walletAddress).first()

    if existing_wallet:
        logger.info(f"Updating existing wallet: {request.personalData.walletAddress}")
        existing_wallet.private_key = request.backendPrivateKey
        session.commit()
        return {"message": "Wallet private key updated successfully."}

    new_wallet = UserWallet(
        wallet_address=request.personalData.walletAddress,
        private_key=request.backendPrivateKey,
        created_at=datetime.utcnow()
    )

    session.add(new_wallet)
    session.commit()
    logger.info(f"Successfully registered new wallet: {request.personalData.walletAddress}")

    return {"message": "External data and private key received successfully."}
