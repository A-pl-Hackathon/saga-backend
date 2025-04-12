from pydantic import BaseModel

class PersonalData(BaseModel):
    walletAddress: str
    data: str

class ExternalData(BaseModel):
    personalData: PersonalData
    agentModel: str
    backendPrivateKey: str  # 추가된 필드
