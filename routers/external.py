from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

# 데이터 수신 형태 정의
class PersonalData(BaseModel):
    wallet_address: str = Field(..., alias="wallet-address")
    data: str

class ExternalRequest(BaseModel):
    apiKey: str
    personal_data: PersonalData = Field(..., alias="personal-data")

@router.post("/external")
async def receive_external_data(request: ExternalRequest):
    print("받은 데이터:", request.dict())
    # 현재는 아무 작업 없이 단순 수신만 합니다.
    return {"status": "success"}
