from pydantic import BaseModel

class TransferRequest(BaseModel):
    amount: str
    schemeName: str
    identification: str
    name: str
    secIdentif: str