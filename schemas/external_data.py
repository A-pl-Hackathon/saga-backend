from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    walletAddress: str
    data: str

class ExternalData(BaseModel):
    personalData: PersonalData
    agentModel: str
