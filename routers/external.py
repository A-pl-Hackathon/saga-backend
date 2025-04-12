from fastapi import APIRouter
from schemas.external_data import ExternalData

router = APIRouter()

@router.post("/external")
async def receive_external_data(request: ExternalData):
    print(request.personalData.walletAddress)
    print(request.personalData.data)
    print(request.agentModel)

    # 추가적인 로직 처리 가능

    return {"message": "Data received successfully"}
